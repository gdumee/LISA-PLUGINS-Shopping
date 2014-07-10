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

Version = "1.0.0"

#TODO



#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------

from lisa.server.plugins.IPlugin import IPlugin
from lisa.Neotique.Neo import NeoTrad


import gettext
import inspect
import os




#-----------------------------------------------------------------------------
# Plugin Shopping class
#-----------------------------------------------------------------------------
class Shopping(IPlugin):
    def __init__(self):

        super(Shopping, self).__init__()

        self.configuration_plugin = self.mongo.lisa.plugins.find_one({"name": "Shopping"})
        self.path = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile(inspect.currentframe()))[0],os.path.normpath("../lang/"))))
        self._ = translation = gettext.translation(domain='shopping',localedir=self.path,fallback=True,languages=[self.configuration_lisa['lang']]).ugettext
        self._ = NeoTrad(self._).Trad
        
        
        #self.build_default_list()
        #self.deletealllist()
        self.answer = None


#-----------------------------------------------------------------------------
    def build_default_list(self):
        shoppingList = self.mongo.lisa.plugins.find_one({'_id': self.configuration_plugin['_id'], "lists.DefaultList": {"$exists": True}})
        if not shoppingList:
            self.mongo.lisa.plugins.update(
                 {'_id': self.configuration_plugin['_id']},{"$set": {
                         'lists.DefaultList.name': 'DefaultList',
                         'lists.DefaultList.items': []
                     }}, upsert=True)
#-----------------------------------------------------------------------------
    def deletealllist(self):
        #delete
        self.mongo.lisa.plugins.update(
            {'_id': self.configuration_plugin['_id']},
            {"$unset": {
            'lists': ''
            }},upsert=True)



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
            namlist=namlist.encode('utf8')
        except:
            return {"plugin": "Shopping",
                "method": "newlist",
                "body": self._('cant create without name')}                 #fatal

        # check if list already  exist
        if self.mongo.lisa.plugins.find_one({'_id': self.configuration_plugin['_id'], 'lists.'+namlist: {"$exists": True}}) is not None:
            return {"plugin": "Shopping",
                "method": "newlist",
                "body": self._('duplicate name')}                 #fatal
        
        #add into db
        self.mongo.lisa.plugins.update({'_id': self.configuration_plugin['_id']},
            {"$set": {
            'lists.'+ namlist + '.name': namlist,
            'lists.'+ namlist + '.items': []
            }},upsert=True)
        smessage = self._('create list').format(namlist)
        return {"plugin": "Shopping",
                "method": "newlist",
                "body": smessage}



#-----------------------------------------------------------------------------
    def deletelist(self,jsonInput):
        """
        delete  exiting list in db
        """
        # Config list name
        try:
            namlist = jsonInput['outcome']['entities']['message_subject']['value']
        except:
            return {"plugin": "Shopping", "method": "deletelist", "body": self._('cant delete without name')}                 #fatal

        # check if list  exist
        if self.mongo.lisa.plugins.find_one({'_id': self.configuration_plugin['_id'], 'lists.'+namlist: {"$exists": True}}) is None:
            return {"plugin": "Shopping", "method": "deletelist","body": self._('no exiting name')}                 #fatal
        
        #delete
        self.mongo.lisa.plugins.update(
            {'_id': self.configuration_plugin['_id']},
            {"$unset": {
            'lists.'+namlist : ''
            }},upsert=True)
        self.answer = self._('delete list') % (namlist)
        return {"plugin": "Shopping", "method": "deletelist","body": self.answer}


#-----------------------------------------------------------------------------
    def getlist(self, jsonInput):
        """
        list all list or all item in a list
        """
        
        #check if any list exist
        shoppingList = self.mongo.lisa.plugins.find_one({'_id': self.configuration_plugin['_id'], "lists": {"$exists": True}})
        if shoppingList is None:
            return {"plugin": "Shopping",
                "method": "getlist",
                "body": self._('no list')}           #fatal

        print 'jsonInput           ',jsonInput
        # Config list name
        namlist=''
        try:
            namlist = jsonInput['outcome']['entities']['message_subject']['value']
        except:
            pass
        
        if namlist <>'':    #list all item in selected list
            self.answer=''
            # check if selected list  exist
            if self.mongo.lisa.plugins.find_one({'_id': self.configuration_plugin['_id'], 'lists.'+namlist: {"$exists": True}}) is None:
                return {"plugin": "Shopping",
                    "method": "getlist",
                    "body": self._('no exiting name')}                 #fatal
                        
            listitem = []
            for item in shoppingList['lists'][namlist]['items']:
                if item['quantity']>0 :
                    listitem.append(str(item['quantity']) + ' ' + item['name'])
                else:
                    listitem.append(item['name'])
            #self.answer += self._(' then ').join(listitem)
            self.answer = self._('product in list').format(slist=namlist,sproduct=', '.join(listitem))

            return {"plugin": "Shopping", "method": "getlist","body": self.answer}
        
        else :  #list all existing list
            self.answer=''
            for item in shoppingList['lists']:
                self.answer += shoppingList['lists'][item]['name'] +','
            self.answer = self._('known list').format (slist=self.answer)
            return {"plugin": "Shopping","method": "getlist", "body": self.answer}
        
        
#-----------------------------------------------------------------------------
    def add(self, jsonInput):
        
        #print "json             ", jsonInput
        item =''
        namlist=''
        qty =0
        try :
            item = jsonInput['outcome']['entities']['shopping_item']['value']
            namlist = jsonInput['outcome']['entities']['message_subject']['value']
            qty = int(jsonInput['outcome']['entities']['number']['value'])
        except:
            if item =='' :                       #fatal
                return {"plugin": "Shopping",
                    "method": "newlist",
                    "body": self._('no item')}
            if namlist =='' :                       #fatal
                return {"plugin": "Shopping",
                    "method": "newlist",
                    "body": self._('no exiting name')}
        
        # check if list  exist
        if self.mongo.lisa.plugins.find_one({'_id': self.configuration_plugin['_id'], 'lists.'+namlist: {"$exists": True}}) is None:
            return {"plugin": "Shopping",
                "method": "newlist",
                "body": self._('no exiting name')}                 #fatal
        
        #add into the db
        self.mongo.lisa.plugins.update(
            {'_id': self.configuration_plugin['_id']},{
                '$addToSet': {'lists.'+ namlist + '.items': { 'name':item,'quantity':qty}},
            },
            upsert=True
        )
        return {"plugin": "Shopping",
                "method": "add",
                "body": self._('product added to the list').format(product=item)
        }

#-----------------------------------------------------------------------------
    def delete(self, jsonInput):
        
        item =''
        namlist=''
        try :
            item = jsonInput['outcome']['entities']['shopping_item']['value']
            namlist = jsonInput['outcome']['entities']['message_subject']['value']
        except:
            if item =='' :                       #fatal
                return {"plugin": "Shopping",
                    "method": "delete",
                    "body": self._('no item')}
            if namlist =='' :                       #fatal
                return {"plugin": "Shopping",
                    "method": "delete",
                    "body": self._('no exiting name')}
        
        #check if list exist
        shoppingList = self.mongo.lisa.plugins.find_one({'_id': self.configuration_plugin['_id'], "lists": {"$exists": True}})
        if shoppingList is None:
            return {"plugin": "Shopping",
                "method": "list",
                "body": self._('no list')}           #fatal
        
        # check if item  exist
        listitem = []
        itemexist = False
        for item2 in shoppingList['lists'][namlist]['items']:
            if item2['name'] == item :
                itemexist = True

        if itemexist == False :
            return {"plugin": "Shopping",
                "method": "delete",
                "body": self._('no product to delete').format(sproduct=item, slist=namlist)           #fatal
            }
        
        #delete item
        self.mongo.lisa.plugins.update({'_id': self.configuration_plugin['_id']},
            {
                '$pull': {'lists.'+ namlist + '.items': {'name': item}}
            },upsert=True)
            
        return {"plugin": "Shopping",
                "method": "delete",
                "body": self._('product deleted').format(sproduct=item)
        }
        
#-----------------------------------------------------------------------------
#              privates functions
#-----------------------------------------------------------------------------




#-----------------------------------------------------------------------------
# Tests
#-----------------------------------------------------------------------------

if __name__ == "__main__" :
          
    jsonInput = {'from': u'Lisa-Web', 'zone': u'WebSocket', u'msg_id': u'c7e169a5-9d87-4a43-8a11-9fa75fd0e5ae',
        u'msg_body': u'fait une nouvelle liste pour les courses',
        u'outcome':  {
            u'entities': {
                u'message_subject': {u'body': u'les courses', u'start': 30, u'end': 41, u'suggested': True, u'value': u'les courses3'}},
            u'confidence': 0.585, 
            u'intent': u'shopping_newlist'},
        'type': u'chat'}

    jsonInput2 = {'from': u'Lisa-Web', 'zone': u'WebSocket', u'msg_id': u'c7e169a5-9d87-4a43-8a11-9fa75fd0e5ae',
        u'msg_body': u'supprime la liste pour les courses',
        u'outcome':  {
            u'confidence': 0.585, 
            u'intent': u'shopping_deletelist'},
        'type': u'chat'}

    jsonInputadd = {'from': u'Lisa-Web', 'zone': u'WebSocket', u'msg_id': u'97c99d41-37d9-4811-95e0-6a5c89d7e1ad', 
        u'msg_body': u'rajoute six pack de lait  dans la liste les courses3', 
        u'outcome': {
            u'entities': {
                u'shopping_item': {u'body': u'pack de lait', u'start': 12, u'end': 24, u'suggested': True, u'value': u'PQ'}, 
                u'number': {u'body': u'six', u'start': 8, u'end': 11, u'value': 2}, 
                u'message_subject': {u'body': u'des choses \xe0 acheter', u'start': 40, u'end': 60, u'suggested': True, u'value': u'les courses3'}
                }, 
            u'confidence': 0.963, 
            u'intent': u'shopping_add'
            }, 
        'type': u'chat'}


    #retourn = Shopping().newlist(jsonInput)
    #print (retourn['body'])
    #retourn = Shopping().deletelist(jsonInput)
    #retourn = Shopping().add(jsonInputadd)
    retourn = Shopping().delete(jsonInputadd)
    print (retourn['body'])
    #print (retourn['body'])
    retourn = Shopping().getlist(jsonInput)
    print (retourn['body'])
    

    

# --------------------- End of Shopping.py  ---------------------
