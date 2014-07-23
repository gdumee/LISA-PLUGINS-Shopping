# -*- coding: UTF-8 -*-
#-----------------------------------------------------------------------------
# project     : Lisa plugins
# module      : Shopping
# file        : shopping.py
# description : Manage (shopping) lists
# author      : G.Audet
#-----------------------------------------------------------------------------
# copyright   : Neotique
#-----------------------------------------------------------------------------

# TODO :


#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
from lisa.server.plugins.IPlugin import IPlugin
from lisa.Neotique.NeoTrans import NeoTrans
import gettext
import inspect
import os, sys


#-----------------------------------------------------------------------------
# Plugin Shopping class
#-----------------------------------------------------------------------------
class Shopping(IPlugin):
    def __init__(self):
        super(Shopping, self).__init__()

        self.configuration_plugin = self.mongo.lisa.plugins.find_one({"name": "Shopping"})
        self.path = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile(inspect.currentframe()))[0],os.path.normpath("../lang/"))))
        self._ = NeoTrans(domain='shopping',localedir=self.path,fallback=True,languages=[self.configuration_lisa['lang']]).Trans
        self.shoppingList = self.mongo.lisa.plugins.find_one({'_id': self.configuration_plugin['_id'], "lists": {"$exists": True}})


    #-----------------------------------------------------------------------------
    #              Publics  Fonctions
    #-----------------------------------------------------------------------------
    def newlist(self,jsonInput):
        """
        create a nex list in db
        """
        # Config list name
        try:
            namlist = jsonInput['outcome']['entities']['message_subject']['value']
            namlist = namlist.encode('utf8')
        except:
            return {"plugin": __name__.split('.')[-1], "method": sys._getframe().f_code.co_name, "body": self._('cant create without name')}

        # check if list already  exist
        if self._listExist(namlist) is True:
            return {"plugin": __name__.split('.')[-1], "method": sys._getframe().f_code.co_name, "body": self._('duplicate name')}

        #add into db
        self.mongo.lisa.plugins.update({'_id': self.configuration_plugin['_id']},
            {"$set": {
            'lists.'+ namlist + '.name': namlist,
            'lists.'+ namlist + '.items': []
            }},upsert=True)
        smessage = self._('create list').format(namlist)
        return {"plugin": __name__.split('.')[-1], "method": sys._getframe().f_code.co_name, "body": smessage}

    #-----------------------------------------------------------------------------
    def deletelist(self,jsonInput):
        """
        delete  exiting item into a list or a list in db
        """
        #check if any list exist
        if self._anyListExist() is False : 
            return {"plugin": __name__.split('.')[-1], "method": sys._getframe().f_code.co_name, "body": self._('no list')}            #fatal
            
            
        # Config list name
        item =''
        namlist=''
        try :
            namlist = jsonInput['outcome']['entities']['message_subject']['value']
            item = jsonInput['outcome']['entities']['shopping_item']['value']
        except:
            #if item =='' :            no matter
             #   return {"plugin": __name__.split('.')[-1], "method": sys._getframe().f_code.co_name, "body": self._('no item')}
            if namlist =='' :
                return {"plugin": __name__.split('.')[-1], "method": sys._getframe().f_code.co_name, "body": self._('no exiting name')}
        

        # check if selected list  exist
        message=''
        if self._listExist(namlist) is False:
            message = self._('no exiting name') + ' '
            message += self._listAll()
            return {"plugin": __name__.split('.')[-1], "method": sys._getframe().f_code.co_name, "body": message}                     #fatal

        
        #if listExist == True : 
        if item =='' :
            #delete list
            self.mongo.lisa.plugins.update(
            {'_id': self.configuration_plugin['_id']},
            {"$unset": {'lists.'+namlist : ''}},upsert=True)
            message = self._('delete list').format(namlist)
        else :
            # check if item  exist
            listitem = []
            itemexist = False
            for item2 in self.shoppingList['lists'][namlist]['items']:
                if item2['name'] == item :
                    itemexist = True
                    break
                    
            if itemexist == True :
                #delete item
                self.mongo.lisa.plugins.update({'_id': self.configuration_plugin['_id']},
                    {'$pull': {'lists.'+ namlist + '.items': {'name': item}}},upsert=True)
                message = self._('product deleted').format(sproduct = item)
            else:
                message = self._('no product to delete').format(sproduct = item, slist = namlist)

        return {"plugin": __name__.split('.')[-1], "method": sys._getframe().f_code.co_name,"body": message}
        
    #-----------------------------------------------------------------------------
    def getlist(self, jsonInput):
        """
        list all list or all item in a list
        """
        #check if any list exist
        if self._anyListExist() is False : 
            return {"plugin": __name__.split('.')[-1], "method": sys._getframe().f_code.co_name, "body": self._('no list')}            #fatal

        # Config list name
        namlist=''
        try:
            namlist = jsonInput['outcome']['entities']['message_subject']['value']
        except:
            pass
        
        # check if selected list  exist
        message=''
        if self._listExist(namlist) is False:
            message = self._('no exiting name') + ' '
            message += self._listAll()
        else :   
            #list all item in selected list
            listitem = []
            for item in self.shoppingList['lists'][namlist]['items']:
                if item['quantity']>0 :
                    listitem.append(str(item['quantity']) + ' ' + item['name'])
                else:
                    listitem.append(item['name'])
            message = self._('product in list').format(slist = namlist, sproduct = ', '.join(listitem)) 
            
        return {"plugin": __name__.split('.')[-1], "method": sys._getframe().f_code.co_name, "body": message}

    #-----------------------------------------------------------------------------
    def add(self, jsonInput):
        """
        add an tiem into a existing list
        """
        #check if any list exist
        if self._anyListExist() is False : 
            return {"plugin": __name__.split('.')[-1], "method": sys._getframe().f_code.co_name, "body": self._('no list')}            #fatal
        
        # Config
        item =''
        namlist=''
        qty =0
        try :
            qty = int(jsonInput['outcome']['entities']['number']['value'])
            item = jsonInput['outcome']['entities']['shopping_item']['value']
            namlist = jsonInput['outcome']['entities']['message_subject']['value']
        except:
            if item =='' :
                return {"plugin": __name__.split('.')[-1], "method": sys._getframe().f_code.co_name, "body": self._('no item')}            #fatal
            if namlist =='' and len(self.shoppingList['lists'])>1:   #special case if juste one list : add to this list
                return {"plugin": __name__.split('.')[-1], "method": sys._getframe().f_code.co_name, "body": self._('no exiting name')}            #fatal
            #if qty -> no matter
        
        
        #special case if juste one list (len(self.shoppingList['lists'])==1) ): add to this list
        if len(self.shoppingList['lists'])==1 :
            for item2 in self.shoppingList['lists']:
                namlist = self.shoppingList['lists'][item2]['name']

        
        # check if selected list  exist
        if self._listExist(namlist) is False:
            message = self._('no exiting name') + ' '
            message += self._listAll()
        else :   
            #add into the db
            self.mongo.lisa.plugins.update(
                {'_id': self.configuration_plugin['_id']},{
                    '$addToSet': {'lists.'+ namlist + '.items': { 'name':item,'quantity':qty}},
                },upsert=True)
            message = self._('product added to the list').format(product=item, slist = namlist)
            
            
        return {"plugin": __name__.split('.')[-1], "method": sys._getframe().f_code.co_name, "body": message}
       
       
       
    #-----------------------------------------------------------------------------
    #              Private  Fonctions
    #-----------------------------------------------------------------------------
    def _anyListExist(self):
        """
        check if ANY list  exist
        """
        #if self.mongo.lisa.plugins.find_one({'_id': self.configuration_plugin['_id'], "lists": {"$exists": True}}) is None:
        if self.shoppingList is None :
            return False    
        else :
            return True
    
    #-----------------------------------------------------------------------------
    def _listExist(self, namlist):
        """
        check if selected list exist
        """
        if self.mongo.lisa.plugins.find_one({'_id': self.configuration_plugin['_id'], 'lists.'+namlist: {"$exists": True}}) is None:
            return False    
        else :
            return True
            
        
    #-----------------------------------------------------------------------------
    def _listAll(self):
        """
        list all existing list into db
        """
        ret=''
        for item in self.shoppingList['lists']:
            ret += self.shoppingList['lists'][item]['name'] +','
        return self._('known list').format(slist = ret) 
                
            
    #-----------------------------------------------------------------------------
    def build_default_list(self):  #for test only
        shoppingList = self.mongo.lisa.plugins.find_one({'_id': self.configuration_plugin['_id'], "lists.DefaultList": {"$exists": True}})
        if not shoppingList:
            self.mongo.lisa.plugins.update(
                 {'_id': self.configuration_plugin['_id']},{"$set": {
                         'lists.DefaultList.name': 'DefaultList',
                         'lists.DefaultList.items': []
                     }}, upsert=True)

    #-----------------------------------------------------------------------------
    def deletealllist(self):   #for test only
        #delete
        self.mongo.lisa.plugins.update(
            {'_id': self.configuration_plugin['_id']},
            {"$unset": {
            'lists': ''
            }},upsert=True)
    
    



#-----------------------------------------------------------------------------
# Tests
#-----------------------------------------------------------------------------
if __name__ == "__main__" :

    jsonInput = {'from': u'Lisa-Web', 'zone': u'WebSocket', u'msg_id': u'c7e169a5-9d87-4a43-8a11-9fa75fd0e5ae',
        u'msg_body': u'fait une nouvelle liste pour les courses',
        u'outcome':  {
            u'entities': {
                u'message_subject': {u'body': u'les courses', u'start': 30, u'end': 41, u'suggested': True, u'value': u'les courses'}},
            u'confidence': 0.585,
            u'intent': u'shopping_newlist'},
        'type': u'chat'}

    jsonInput2 = {'from': u'Lisa-Web', 'zone': u'WebSocket', u'msg_id': u'c7e169a5-9d87-4a43-8a11-9fa75fd0e5ae',
        u'msg_body': u'supprime la liste pour les courses',
        u'outcome':  {
            u'entities': {
                u'shopping_item': {u'body': u'pack de lait', u'start': 12, u'end': 24, u'suggested': True, u'value': u'PQ'},
                u'message_subject': {u'body': u'des choses \xe0 acheter', u'start': 40, u'end': 60, u'suggested': True, u'value': u'les courses'}
                },
            u'confidence': 0.585,
            u'intent': u'shopping_delete'},
        'type': u'chat'}

    jsonInputadd = {'from': u'Lisa-Web', 'zone': u'WebSocket', u'msg_id': u'97c99d41-37d9-4811-95e0-6a5c89d7e1ad',
        u'msg_body': u'rajoute six pack de lait  dans la liste les courses3',
        u'outcome': {
            u'entities': {
                u'shopping_item': {u'body': u'pack de lait', u'start': 12, u'end': 24, u'suggested': True, u'value': u'beurre'},
                u'number': {u'body': u'six', u'start': 8, u'end': 11, u'value': 2},
                u'message_subject': {u'body': u'des choses \xe0 acheter', u'start': 40, u'end': 60, u'suggested': True, u'value': u'les courses2'}
                },
            u'confidence': 0.963,
            u'intent': u'shopping_add'
            },
        'type': u'chat'}
    
    jsonInputadd2 = {'from': u'Lisa-Web', 'zone': u'WebSocket', u'msg_id': u'97c99d41-37d9-4811-95e0-6a5c89d7e1ad',
    u'msg_body': u'rajoute six pack de lait  dans la liste les courses3',
    u'outcome': {
        u'entities': {
            u'shopping_item': {u'body': u'pack de lait', u'start': 12, u'end': 24, u'suggested': True, u'value': u'PQ'},
            u'number': {u'body': u'six', u'start': 8, u'end': 11, u'value': 2},
            },
        u'confidence': 0.963,
        u'intent': u'shopping_add'
        },
    'type': u'chat'}
    
    essais = Shopping()
    #retourn = essais.newlist(jsonInput)
    #retourn = essais.deletelist(jsonInput)
    #retourn = essais.add(jsonInputadd2)
    retourn = essais.deletelist(jsonInputadd)
    print (retourn['body'])
    
    retourn = essais.getlist(jsonInput)
    print (retourn['body'])

# --------------------- End of shopping.py  ---------------------
