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
#Mandatory
from lisa.server.plugins.IPlugin import IPlugin
from lisa.Neotique.NeoTrans import NeoTrans
import gettext
import inspect
import os, sys

#ohters

#-----------------------------------------------------------------------------
# Plugin Shopping class
#-----------------------------------------------------------------------------
class Shopping(IPlugin):
    def __init__(self):
        #super(Shopping, self).__init__(plugin_name = "Shopping")
        
        
        super(Shopping, self).__init__()
        self.configuration_plugin = self.mongo.lisa.plugins.find_one({"name": "Shopping"})
        self.path = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile(inspect.currentframe()))[0],os.path.normpath("../lang/"))))
        self._ = NeoTrans(domain='shopping',localedir=self.path,fallback=True,languages=[self.configuration_lisa['lang']]).Trans
        
        

        #self.shoppingList = self.mongo.lisa.plugins.find_one({'_id': self.configuration_plugin['_id'], "lists": {"$exists": True}})
        self.shoppingList = self.mongo.lisa.plugins.find_one({"name": "Shopping", "lists": {"$exists": True}})
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
            return {"plugin": __name__.split('.')[-1], "method": sys._getframe().f_code.co_name, "body": self._('cant create without name'),"test":"no-name"}

        # check if list already  exist
        if self._listExist(namlist) is True:
            return {"plugin": __name__.split('.')[-1], "method": sys._getframe().f_code.co_name, "body": self._('duplicate name'),"test":"duplicate"}

        #add into db
        self.mongo.lisa.plugins.update({'_id': self.configuration_plugin['_id']},
            {"$set": {
            'lists.'+ namlist + '.name': namlist,
            'lists.'+ namlist + '.items': []
            }},upsert=True)
        smessage = self._('create list').format(namlist)
        return {"plugin": __name__.split('.')[-1], "method": sys._getframe().f_code.co_name, "body": smessage,"test":"new"}

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
            #if item =='' :    no matter
            if namlist =='' :
                return {"plugin": __name__.split('.')[-1], "method": sys._getframe().f_code.co_name, "body": self._('no exiting name'),'test':'no-namelist'}
        

        # check if selected list  exist
        message=''
        if self._listExist(namlist) is False:
            message = self._('no exiting name') + ' '
            message += self._listAll()
            return {"plugin": __name__.split('.')[-1], "method": sys._getframe().f_code.co_name, "body": message,'test':'no-existing'}                     #fatal

        
        #if listExist == True : 
        if item =='' :
            #delete list
            self.mongo.lisa.plugins.update(
            {'_id': self.configuration_plugin['_id']},
            {"$unset": {'lists.'+namlist : ''}},upsert=True)
            message = self._('delete list').format(namlist)
            test ='del-list'
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
                test = 'product'
            else:
                message = self._('no product to delete').format(sproduct = item, slist = namlist)
                test = 'no-product'

        return {"plugin": __name__.split('.')[-1], "method": sys._getframe().f_code.co_name,"body": message,'test':test}
        
    #-----------------------------------------------------------------------------
    def getlist(self, jsonInput):
        """
        list all list or all item in a list
        """
        #check if any list exist
        if self._anyListExist() is False : 
            return {"plugin": __name__.split('.')[-1], "method": sys._getframe().f_code.co_name, "body": self._('no list'),"test":"no-list"}            #fatal

        # Config list name
        namlist=''
        try:
            namlist = jsonInput['outcome']['entities']['message_subject']['value']
        except:
            pass
        
        # check if selected list  exist
        message=''
        listitem=''
        if self._listExist(namlist) is False:
            message = self._('no exiting name') + ' '
            message += self._listAll()
            test = 'no-existing'
        else :   
            #list all item in selected list
            listitem = []
            for item in self.shoppingList['lists'][namlist]['items']:
                if item['quantity']>0 :
                    listitem.append(str(item['quantity']) + ' ' + item['name'])
                else:
                    listitem.append(item['name'])
            message = self._('product in list').format(slist = namlist, sproduct = ', '.join(listitem)) 
            test = listitem
            
        return {"plugin": __name__.split('.')[-1], "method": sys._getframe().f_code.co_name, "body": message,'test':test}

    #-----------------------------------------------------------------------------
    def add(self, jsonInput):
        """
        add an tiem into a existing list
        """
        #check if any list exist
        if self._anyListExist() is False : 
            return {"plugin": __name__.split('.')[-1], "method": sys._getframe().f_code.co_name, "body": self._('no list'),'test':'no-list'}            #fatal
        
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
                return {"plugin": __name__.split('.')[-1], "method": sys._getframe().f_code.co_name, "body": self._('no item'),'test':'no-item'}            #fatal
            if namlist =='' and len(self.shoppingList['lists'])>1:   #special case if juste one list : add to this list
                return {"plugin": __name__.split('.')[-1], "method": sys._getframe().f_code.co_name, "body": self._('no exiting name'),'test':'no-list'}            #fatal
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
            
            
        return {"plugin": __name__.split('.')[-1], "method": sys._getframe().f_code.co_name, "body": message,'test':'add'}
       
       
       
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
                


# --------------------- End of shopping.py  ---------------------
