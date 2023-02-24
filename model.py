import pymongo


# Connexion MongoDB
class MongoConnection:
    __instance = None

    @staticmethod
    def getInstance():
        if MongoConnection.__instance is None:
            connection_string = 'mongodb+srv://riperpro:IBkTL4m1H4zZvzsl@cluster0.urnuehu.mongodb.net' \
                                '/BD_DataVisualizer?retryWrites=true&w=majority'
            client = pymongo.MongoClient(connection_string)
            bd = client['BD_DataVisualizer']
            MongoConnection.__instance = bd
        return MongoConnection.__instance


# Essai
class Essai:
    def __init__(self, id, registry, dateInserted, dateIntervention, linkout, gender, conditions, acronym, titre,
                 abstract, phase, observationnelles, Randomise, interventions):
        self.id = id
        self.registry = registry
        self.dateInserted = dateInserted
        self.dateIntervention = dateIntervention
        self.linkout = linkout
        self.gender = gender
        self.conditions = conditions
        self.acronym = acronym
        self.titre = titre
        self.abstract = abstract
        self.phase = phase
        self.observationnelles = observationnelles
        self.Randomise = Randomise
        self.interventions = interventions

    def getDict(self):
        return {"_id": self.id,
                "registry": self.registry,
                "dateInserted": self.dateInserted,
                "dateIntervention": self.dateIntervention,
                "linkout": self.linkout,
                "gender": self.gender,
                "conditions": self.conditions,
                "acronym": self.acronym,
                "titre": self.titre,
                "abstract": self.abstract,
                "phase": self.phase,
                "observationnelles": self.observationnelles,
                "Randomise": self.Randomise,
                "interventions": self.interventions
                }

    def __str__(self):
        return str(self.getDict())


# Intervention
class Intervention:
    def __init__(self, name, description, other_names, arm_group_labels, type):
        self.name = name
        self.description = description
        self.other_names = other_names
        self.arm_group_labels = arm_group_labels
        self.type = type

    def getDict(self):
        return {"name": self.name,
                "description": self.description,
                "other_names": self.other_names,
                "armGroupLabels": self.arm_group_labels,
                "type": self.type}

    def __str__(self):
        return str(self.getDict())
