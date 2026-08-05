import random
import numpy as np 

class Station:
  def __init__(self, name):
    self.name= name
    self.connections = [] #list, append
    self.passengers = 0
    self.congestion = 0
  
  def addConnection(self, connection):
    self.connections.append(connection)
  
  def __str__(self):
    return self.name


class Connection:
  def __init__(self, destination, travelTime, line):
    self.destination = destination
    self.travelTime = travelTime
    self.line = line
    self.delay = 0
    self.closed = False
  
  def __str__(self):
    return f"{self.destination}({self.travelTime} mins,{self.line})"

class UndergroundNetwork:
  def __init__(self):
    self.stations = {} #dictionary
  
  def addStation(self, name):
    if name not in self.stations:
      self.stations[name] =Station(name)
  
  def addConnection(self, station1, station2, time, line):
    s1 = self.stations[station1]
    s2 = self.stations[station2]
    
    s1.addConnection(
      Connection(s2, time, line) #direction 1
    )

    s2.addConnection(
      Connection(s1, time, line) #direction 2
    )
  
  def display(self, name):
    station = self.stations[name]
    print(f"\n{name}")

    for i in station.connections:
      print(" ->", i)
  
  def findRoute(self, start, destination):
    distances = {}
    previous = {}
    unvisited = []

    for station in self.stations:
        distances[station] = float("inf")
        previous[station] = None
        unvisited.append(station)
    distances[start] = 0
    while unvisited:
        current = min(
            unvisited,
            key=lambda station: distances[station]
        )
        if current == destination:
            break

        unvisited.remove(current)
        current_station = self.stations[current]

        for connection in current_station.connections:
            neighbour = connection.destination.name
            new_distance = (
                distances[current]
                + connection.travelTime
            )
            if new_distance < distances[neighbour]:

                distances[neighbour] = new_distance
                previous[neighbour] = current
    route = []

    current = destination

    while current is not None:
        route.append(current)
        current = previous[current]
    route.reverse()

    return route
  
  def simulateJourney(self, route):
    delayModel = Delay()
    total = 0

    for i, j in zip(route, route[1:]): #i= current station, j= next
      station = self.stations[i]
      for x in station.connections:
        if x.destination.name == j:
          delayModel.updateState()
          delay = delayModel.generateDelay()
          total+= x.travelTime +delay

          break
    return total
  
  def monteCarlo(self, route, simulations):
    results = []
    for i in range(simulations):
      time = self.simulateJourney(route)
      results.append(time)
    return results

class Delay:
  def __init__(self):
    self.state = "Normal"

  def generateDelay(self):
    if self.state == "Normal":
      return random.expovariate(2) #poisson model, 1/lambd
    elif self.state =="Minor":
      return random.expovariate(0.5)
    else: #Major
      return random.expovariate(0.2)
  
  def updateState(self):
    if self.state == "Normal":
      weights = [95,4,1]
    elif self.state == "Minor":
      weights = [80,15, 5]
    elif self.state == "Major":
      weights = [40,40, 20]
    
    self.state = random.choices(
      ["Normal", "Minor", "Major"],
      weights=weights
    )[0]

class Insurance:
  def __init__(self, threshold, payout):
    self.threshold = int(threshold)
    self.payout = int(payout)
  
  def calcPayout(self, journeyTime):
    if int(journeyTime) > self.threshold:
      return self.payout
    else:
      return 0


network = UndergroundNetwork()
victoriaStations = [
  "Brixton",
  "Stockwell",
  "Vauxhall",
  "Pimlico",
  "Victoria",
  "Green Park",
  "Oxford Circus",
  "Warren Street",
  "Euston",
  "King's Cross St.Pancras",
  "Highbury & Islington",
  "Finsbury Park",
  "Seven Sisters",
  "Tottenham Hale",
  "Blackhorse Road",
  "Walthamstow Central"
]

for i in victoriaStations: #add stations to dictionary
  network.addStation(i)

network.addConnection("Brixton", "Stockwell", 2, "Victoria")
network.addConnection("Stockwell","Vauxhall", 2, "Victoria")
network.addConnection("Vauxhall","Pimlico", 2, "Victoria")
network.addConnection("Pimlico","Victoria", 2, "Victoria")
network.addConnection("Victoria","Green Park", 2, "Victoria")
network.addConnection("Green Park","Oxford Circus", 2, "Victoria")
network.addConnection("Oxford Circus", "Warren Street", 2, "Victoria")
network.addConnection("Warren Street","Euston", 1, "Victoria")
network.addConnection("Euston","King's Cross St.Pancras", 2, "Victoria")
network.addConnection("King's Cross St.Pancras","Highbury & Islington", 3, "Victoria")
network.addConnection("Highbury & Islington","Finsbury Park", 2, "Victoria")
network.addConnection("Finsbury Park","Seven Sisters", 3, "Victoria")
network.addConnection("Seven Sisters","Tottenham Hale", 2, "Victoria")
network.addConnection("Tottenham Hale","Blackhorse Road", 2, "Victoria")
network.addConnection("Blackhorse Road","Walthamstow Central", 2, "Victoria")

#network.display("Stockwell")
route = network.findRoute("Victoria", "Euston")
print(route)

journey = network.simulateJourney(route)
print(journey)

results = network.monteCarlo(route, 10000)
print(results[:5])

print("Mean:", np.mean(results))
print("Std:", np.std(results))
print("95% VaR:", np.percentile(results,95))
var95 = np.percentile(results,95)
tail = [x for x in results if x > var95]
print("Expected Shortfall:", np.mean(tail))

premium = 2
insurance = Insurance(13, 10) #pays £10 if journey over 13 mins
payouts = []

for j in results:
  payout = insurance.calcPayout(j)
  payouts.append(payout)

print(payouts[:5])

expectedPayout = sum(payouts)/len(payouts)
print(expectedPayout) #avg money insurer loses per passenger

profit = premium - expectedPayout
print(profit)

claimProbability = sum(
  1 for p in payouts if p>0
)/len(payouts)

print(claimProbability) #probability of payout
