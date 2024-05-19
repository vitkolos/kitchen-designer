import pyomo.environ as pyo
database = ['sink', 'fridge', 'dishwasher', 'stove']
length = 60
minWidths = {'sink': 10, 'fridge': 15, 'dishwasher': 15, 'stove': 10}
maximizeWidth = {'sink': 0, 'fridge': 0, 'dishwasher': 0, 'stove': 1}
edgeItem = {'sink': 0, 'fridge': 0, 'dishwasher': 0, 'stove': 0}
segments = list(range(5))
edgeSegment = [0 if x == 0 else 0 for x in segments]
bannedItem = {'sink': 0, 'fridge': 0, 'dishwasher': 0, 'stove': 0}
itemsInZone = {'sink': 0, 'fridge': 1, 'dishwasher': 1, 'stove': 1}

bannedZoneLeft = 0
bannedZoneWidth = 48

model = pyo.ConcreteModel()
model.present = pyo.Var(database, within=pyo.Binary)
model.widths = pyo.Var(segments, bounds=(0, length))
model.previousWidths = pyo.Var(segments, bounds=(0,length))
model.previousDiff = pyo.Var(segments, bounds=(0,length))
model.previousLarger = pyo.Var(segments, within=pyo.Binary)
model.xCoords = pyo.Var(segments, bounds=(0, length))
model.itemWidths = pyo.Var(database, bounds=(0, length))
model.itemXCoords = pyo.Var(database, bounds=(0, length))
model.pairs = pyo.Var(segments, database, within=pyo.Binary)
model.bannedZoneSide = pyo.Var(database, within=pyo.Binary)
# model.zoneCenter = pyo.Var(bounds=(0, length))
# https://math.stackexchange.com/a/2753629

# požadavek na minimální šířku spotřebičů
def minItemWidth(model, segment, item):
    return model.widths[segment] >= (minWidths[item]*model.pairs[segment, item])


# zakázání prázdných segmentů nenulové délky
def noEmptySegments(model, segment):
    return model.widths[segment] <= (1000 * sum(model.pairs[segment, item] for item in database))


# provázání mezi přítomností a páry
def presencePairsPairing(model, item):
    return sum(model.pairs[segment, item] for segment in segments) == model.present[item]


# na každém segmentu jeden prvek
def maxOneItemAtSegment(model, segment):
    return sum(model.pairs[segment, item] for item in database) <= 1


# krajní segment
def edgeSegments(model, segment, item, clause):
    match clause:
        case 0: return edgeSegment[segment]*model.pairs[segment, item] <= edgeItem[item]
        case 1: return edgeSegment[segment] <= sum(model.pairs[segment, item2] for item2 in database)

# zakazuje určitý typ položek na určitém místě
def banItems(model, item, clause):
    # segmenty se překrývají <=> levý okraj nebo pravý okraj jednoho je mezi okraji druhého
    # segmenty se nepřekrývají <=> pravý okraj jednoho < levý okraj druhého || levý okraj jednoho > pravý okraj druhého
    match clause:
        case 0: return (model.itemXCoords[item] + model.itemWidths[item])*bannedItem[item] <= bannedZoneLeft + length*model.bannedZoneSide[item]
        case 1: return (bannedZoneLeft + bannedZoneWidth)*bannedItem[item] <= model.itemXCoords[item] + length*(1-model.bannedZoneSide[item])




# https://towardsdatascience.com/a-comprehensive-guide-to-modeling-techniques-in-mixed-integer-linear-programming-3e96cc1bc03d
    
def getPrevious(model, segment, clause):
    M = length*2
    segmentIsUsed = sum(model.pairs[segment, item] for item in database)
    
    if segment == 0:
        if clause == 1:
            return model.previousDiff[segment] == 0
        else:
            return model.previousWidths[segment] == 0

    previousSegmentIsUsed = sum(model.pairs[segment-1, item] for item in database)

    match clause:
        case 0: return model.previousWidths[segment] >= model.widths[segment-1]
        case -1: return model.previousWidths[segment] <= model.widths[segment-1] + M*(1-previousSegmentIsUsed)
        case -2: return model.previousWidths[segment] >= model.previousWidths[segment-1] - M*previousSegmentIsUsed
        case -3: return model.previousWidths[segment] <= model.previousWidths[segment-1] + M*previousSegmentIsUsed

        case 1: return model.previousDiff[segment] >= 0
        case 2: return model.previousDiff[segment] >= model.previousWidths[segment]-model.widths[segment] - M*(1-segmentIsUsed)
        case 3: return model.previousDiff[segment] >= model.widths[segment]-model.previousWidths[segment] - M*(1-segmentIsUsed)
        case 4: return model.previousDiff[segment] <= model.previousWidths[segment]-model.widths[segment] + M*(1-model.previousLarger[segment])
        case 5: return model.previousDiff[segment] <= model.widths[segment]-model.previousWidths[segment] + M*model.previousLarger[segment]
        case 6: return model.previousDiff[segment] <= M*segmentIsUsed

# definuje vzdálenost segmentu od levého okraje
def xCoords(model, segment):
    return model.xCoords[segment] == sum(model.widths[i] for i in segments if i < segment)


# definuje šířku položky a její vzdálenost zleva
def itemWidths(model, segment, item, clause):
    M = length
    y = model.pairs[segment, item]
    x = model.widths[segment]
    z = model.itemWidths[item]

    x1 = model.xCoords[segment]
    z1 = model.itemXCoords[item]

    match clause:
        case 0: return x-M*(1-y) <= z
        case 1: return z <= x+M*(1-y)
        case 2: return z <= M*model.present[item]

        case 3: return x1-M*(1-y) <= z1
        case 4: return z1 <= x1+M*(1-y)
        case 5: return z1 <= M*model.present[item]


def fitness(model):
    sum = 0

    for item in database:
        sum += model.present[item]

    for segment in segments:
        sum -= model.previousDiff[segment]*0.1

    # for segment in segments:
    #     sum += 2*model.widths[segment]

    for item in database:
        sum += (model.itemWidths[item] * maximizeWidth[item])/20

    return sum


model.value = pyo.Objective(rule=fitness, sense=pyo.maximize)
model.totalWidth = pyo.Constraint(
    expr=sum(model.widths[i] for i in segments) <= length)
model.presencePairsPairing = pyo.Constraint(
    database, rule=presencePairsPairing)
model.maxOneItemAtSegment = pyo.Constraint(segments, rule=maxOneItemAtSegment)
model.minItemWidth = pyo.Constraint(segments, database, rule=minItemWidth)
model.noEmptySegments = pyo.Constraint(segments, rule=noEmptySegments)
model.edgeSegment = pyo.Constraint(
    segments, database, [0, 1], rule=edgeSegments)
model.banItems = pyo.Constraint(database, [0,1], rule=banItems)
model.getPrevious = pyo.Constraint(segments, [-3,-2,-1,0,1,2,3,4,5,6], rule=getPrevious)
model.getXCoords = pyo.Constraint(segments, rule=xCoords)
model.getItemWidths = pyo.Constraint(
    segments, database, [0, 1, 2, 3, 4, 5], rule=itemWidths)


opt = pyo.SolverFactory('glpk')
# opt = pyo.SolverFactory('gurobi_direct')
result_obj = opt.solve(model, tee=True)
model.pprint()


print("\n\n=== RESULT ===\n")

for segment in segments:
    itemPresent = None

    for item in database:
        if pyo.value(model.pairs[segment, item]):
            itemPresent = item

    width = pyo.value(model.widths[segment])
    print(f"segment {segment}, item {itemPresent}, width {width}")
