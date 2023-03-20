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
    def __init__(self, _id, registry, dateInserted, dateIntervention, linkout, gender, conditions, acronym, titre,
                 abstract, phase, observationnelles, Randomise, interventions):
        self._id = _id
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


# Intervention
class Intervention:
    def __init__(self, name, description, other_names, arm_group_labels, type):
        self.name = name
        self.description = description
        self.other_names = other_names
        self.arm_group_labels = arm_group_labels
        self.type = type


# Publication
class Publication:
    def __init__(self, _id, dateInserted, datePublished, doctype, doi, pmid, linkout, timesCited, altmetric, venue,
                 publisher, title, openAccess, concept, meshTerms, observationnelles, randomise, essais, author):
        self._id = _id
        self.dateInserted = dateInserted
        self.datePublished = datePublished
        self.doctype = doctype
        self.doi = doi
        self.pmid = pmid
        self.linkout = linkout
        self.timesCited = timesCited
        self.altmetric = altmetric
        self.venue = venue
        self.publisher = publisher
        self.title = title
        self.openAccess = openAccess
        self.concept = concept
        self.meshTerms = meshTerms
        self.observationnelles = observationnelles
        self.randomise = randomise
        self.essais = essais
        self.author = author
