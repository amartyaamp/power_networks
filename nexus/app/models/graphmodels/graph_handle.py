from app.models.graphmodels.graphdb import SelectionAlgoGraphDB, CoreGraphDB
from flask import current_app


class GraphHandle():
    
    """Business logic for dealing with graph and querying the right graph"""

    def __init__(self):
        
        self.crawldb = SelectionAlgoGraphDB()

        self.coredb = CoreGraphDB()

    def getCrawlNodeStats(self):
        return self.crawldb.countUnresolvedNodes(), self.crawldb.countNextNodesToResolve()

    def getCrawlRelationStats(self):
        return self.crawldb.countUnresolvedRelations(), self.crawldb.countNextRelationsToResolve()

    def getCrawlHyperEdgeNodeStats(self):
        return self.crawldb.countUnresolvedHyperEdgeNodes(), self.crawldb.countNextHyperEdgeNodesToResolve()

    def areCrawlNodesLeft(self):
        n1,n2 = self.getCrawlNodeStats()
        return n1 != 0 ##here the first count can work as we just need to select any node

    def areCrawlHyperEdgeNodesLeft(self):
        n1,n2 = self.getCrawlHyperEdgeNodeStats()
        return n1 != 0 ##here the first count can work as we just need to select any hyper edge node

    def areCrawlRelationsLeft(self):
        r1,r2 = self.getCrawlRelationStats()
        return r2 != 0  ##here the second count works as we just need to select any relation for which the nodes are resolved

    def updateCrawlNode(self, node, uuid):
        self.crawldb.setResolvedWithUUID(node, uuid)

    def updateCrawlRelation(self, rel, uuid):
        self.crawldb.setResolvedWithRELID(self, rel, relid)

    def nextNodeToResolve(self):
        #TODO: remove prints
        node, degree =  self.crawldb.getNearestBestNode()
        print node
        return node ##returns a type py2neo.Node, can be None

    def nextHyperEdgeNodeToResolve(self):
        #TODO: remove prints
        node =  self.crawldb.getNearestBestHyperEdgeNode()
        print 'hyperedgenode selected'
        print node
        return node ##returns a type py2neo.Node, can be None

    def nextRelationToResolve(self):
        rel =  self.crawldb.getNextRelationToResolve()
        return rel ##returns a type py2neo.relation, can be None

    def getNodeListCore(self, uuidList):
        return self.coredb.getListOfNodes(uuidList)

    def insertCoreNodeHelper(self, node):

        ##a very basic necessity of this! 
        ##as uuids and graphs are linked

        from app.models.dbmodels.idtables import Entity
        en = Entity(node['name'])
        en.create()
        uuid = en.uuid

        ##TODO: move uuid to props!
        print 'uuid generated ' +str(uuid) #change this code : TODO

        return self.coredb.insertCoreNodeWrap(node, uuid)


    def insertCoreRelationHelper(self, crawl_rel): 
        ##this relation contains no metadata
        ##but the start and edn nodes contain metadata for uuids against which resolved

        from app.constants import RESOLVEDWITHUUID, RESOLVEDWITHRELID
        
        start_node_uuid = crawl_rel.start_node[RESOLVEDWITHUUID]
        end_node_uuid = crawl_rel.end_node[RESOLVEDWITHUUID]

        from app.models.dbmodels.idtables import Link
        link = Link(crawl_rel.type, start_node_uuid, end_node_uuid)
        link.create()
        relid = link.relid
        
        return self.coredb.insertCoreRelWrap(crawl_rel, start_node_uuid, end_node_uuid, relid)


    def matchRelationsInCore(self, crawl_rel):
        '''
            Returns a list of relations that are almost as same as this crawl_rel object from crawldb
        '''    
        from app.constants import RESOLVEDWITHUUID, RESOLVEDWITHRELID
        
        start_node_uuid = crawl_rel.start_node[RESOLVEDWITHUUID]
        end_node_uuid = crawl_rel.end_node[RESOLVEDWITHUUID]

        return self.coredb.searchRelations(start_node_uuid, crawl_rel.type, end_node_uuid)


    def matchHyperEdgeNodesInCore(self, crawl_obj):
        '''
            Returns a list of hyperedge nodes that are almost as same as this crawl_obj object from crawldb
        '''    
        from app.constants import RESOLVEDWITHUUID, RESOLVEDWITHRELID, RESOLVEDWITHHENID

        return [] ##for now
        
        start_node_uuid = crawl_rel.start_node[RESOLVEDWITHUUID]
        end_node_uuid = crawl_rel.end_node[RESOLVEDWITHUUID]

        return self.coredb.searchRelations(start_node_uuid, crawl_rel.type, end_node_uuid)


    def getTwoVars(self, kind): ##kind is kind of task
        CRAWL_ID_NAME = None ##Property name in crawl graph
        CURR_ID = None ##Session variable

        from app.constants import CRAWL_EN_ID_NAME, CRAWL_REL_ID_NAME, CRAWL_HEN_ID_NAME

        ##TODO: curr_id using getCoreIDName
        
        if kind == 'relation':
            CRAWL_ID_NAME = CRAWL_REL_ID_NAME
            CURR_ID = 'curr_relid'
        elif kind == 'node':
            CURR_ID = 'curr_uuid'
            CRAWL_ID_NAME = CRAWL_EN_ID_NAME
        elif kind == 'hyperedgenode':
            CURR_ID = 'curr_henid'
            CRAWL_ID_NAME = CRAWL_HEN_ID_NAME

        return CRAWL_ID_NAME, CURR_ID


    def areTasksLeft(self, kind): ##kind is kind of task
        
        ans = False

        if kind == 'node':
            ans = self.areCrawlNodesLeft() 
        elif kind=='relation':
            ans = self.areCrawlRelationsLeft()
        elif kind == 'hyperedgenode':
            ans = self.areCrawlHyperEdgeNodesLeft()

        return ans

    def nextTaskToResolve(self, kind):

        '''
            given a kind - node, relation, hyperedge
            calls the appropriate method
            and returns the next graph object to resolve
        '''

        graphobj = None

        if kind == 'relation':
            graphobj =  self.nextRelationToResolve()
        elif kind == 'node':
            graphobj =  self.nextNodeToResolve()
        elif kind == 'hyperedgenode':
            graphobj = self.nextHyperEdgeNodeToResolve() 
        
        return graphobj


    def getCrawlObjectByID(self, kind, id_prop, id_val, isIDString):
        
        '''
            given a crawl_id like _crawl_en_id_ and its value,
            fetches the crawl node from crawldb
        '''

        if kind == 'relation':
            return self.crawldb.getRelationByUniqueID(id_prop, id_val, isIDString)
        elif kind == 'node':
            return self.crawldb.getNodeByUniqueID('entity', id_prop, id_val, isIDString)
        elif kind == 'hyperedgenode':
            return self.crawldb.getNodeByUniqueID('hyperedgenode',id_prop,id_val, isIDString)

        return None


    def copyCrawlObject(self, kind, crawl_obj_original):
        
        '''
            given the kind and the crawl_obj,
            copies the crawl object accrodingly
            node:copies all props, labels and no metadata
            rel: copies all props, label, no relation metadata but meta of connected nodes for identification
        '''

        if kind == 'relation':
            return self.crawldb.copyRelationWithEssentialNodeMeta(crawl_obj_original)
        elif kind == 'node' or kind == 'hyperedgenode':
            return self.crawldb.copyNodeWithoutMeta(crawl_obj_original)

        return None

    def matchPossibleObjects(self, kind, crawl_obj):
        
        '''
            the heart and soul of the verifier task
            the faster this method is the better for the human
            the better this method is the easier for the human
            given a crawl_obj matches those kind of objects in the graph
            and gives possible matches
        '''

        if kind == 'relation':
            return self.matchRelationsInCore(crawl_obj)
        elif kind == 'node':
            matchingUUIDS = [67, 68, 73, 74, 75, 76, 77]
            return self.coredb.getNodeListCore(matchingUUIDS)
        elif kind == 'hyperedgenode':
            return self.matchHyperEdgeNodesInCore(crawl_obj)

        return None #or an empty list?


    def insertCoreGraphObjectHelper(self, kind, crawl_obj):
        
        '''
            based on the kind, creates the graph object
            inserts it in core graph db,
            and returns the corresponding id - uuid, relid, hyperedgeid
        '''

        if kind=='node':
            curr_obj = self.insertCoreNodeHelper(crawl_obj)
            return curr_obj['uuid']
        elif kind == 'relation':
            curr_obj = self.insertCoreRelationHelper(crawl_obj)
            return curr_obj['relid']
        elif kind == 'hyperedgenode':
            curr_obj = self.insertCoreHyperEdgeNodeHelper(crawl_obj)

        return None

    def setResolvedWithID(self, kind, crawl_obj_original, curr_id):
        '''
            based on kind - node, relation, hyperedge, etc.,
            gives a resolveid to the graphobj of crawldb and sets this
            resolveid to the curr_id that we get from the coredb
        '''
        if kind == 'node':
            self.crawldb.setResolvedWithUUID(crawl_obj_original, curr_id)
        elif kind == 'relation':
            self.crawldb.setResolvedWithRELID(crawl_obj_original, curr_id)
        return
        #doesn't return anything just sets resolved ID

    def getCoreIDName(self, kind):

        '''
            given a kind, returns the core id name for that graph object
            relid, uuid, hyperedgeid, etc.
        '''

        if kind == 'node':
            return 'uuid'
        elif kind == 'relation':
            return 'relid'
        elif kind == 'hyperedge':
            return 'henid'

        return None

    def getDirectlyConnectedEntities(self, kind, graphobj):

        if kind == 'hyperedgenode':
            from app.constants import CRAWL_HEN_ID_NAME, LABEL_HYPEREDGE_NODE
            return self.crawldb.getDirectlyConnectedEntities(CRAWL_HEN_ID_NAME, graphobj[CRAWL_HEN_ID_NAME], LABEL_HYPEREDGE_NODE, isIDString = True)

        return None




         