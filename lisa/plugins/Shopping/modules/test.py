# -*- coding: UTF-8 -*-
import unittest
import logging


# Le code à tester doit être importable
from shopping import Shopping

#requiered


class TestNeoConv(unittest.TestCase):
 
    
    # Cette méthode sera appelée avant chaque test.
    def setUp(self):
        pass
        
    # Cette méthode sera appelée après chaque test.
    def tearDown(self):
        pass
        
    def test_0newlist(self):
        test=Shopping().newlist
        jsonInput = {'from': u'Lisa-Web', 'zone': u'WebSocket', u'msg_id': u'c7e169a5-9d87-4a43-8a11-9fa75fd0e5ae',
            u'msg_body': u'do a new list for test',
            u'outcome':  {
                u'entities': {
                    u'message_subject': {u'body': u'test', u'start': 30, u'end': 41, u'suggested': True, u'value': u'test'}},
                u'confidence': 0.585,
                u'intent': u'shopping_newlist'},
            'type': u'chat'}
        ret = test(jsonInput)
        try :
            assert (ret['test'] == 'new')    
        except AssertionError :
            print ret["body"]
            raise AssertionError
            
    def test_0newlistagain(self):
        test=Shopping().newlist
        jsonInput = {'from': u'Lisa-Web', 'zone': u'WebSocket', u'msg_id': u'c7e169a5-9d87-4a43-8a11-9fa75fd0e5ae',
            u'msg_body': u'do the same new list for test',
            u'outcome':  {
                u'entities': {
                    u'message_subject': {u'body': u'les courses', u'start': 30, u'end': 41, u'suggested': True, u'value': u'test'}},
                u'confidence': 0.585,
                u'intent': u'shopping_newlist'},
            'type': u'chat'}
        ret = test(jsonInput)
        try :
            assert (ret['test'] == 'duplicate')    
        except AssertionError :
            print ret["body"]
            raise AssertionError
    
    def test_0newlistnameless(self):
        test=Shopping().newlist
        jsonInput = {'from': u'Lisa-Web', 'zone': u'WebSocket', u'msg_id': u'c7e169a5-9d87-4a43-8a11-9fa75fd0e5ae',
            u'msg_body': u'do new list without name',
            u'outcome':  {
                u'entities': {},
                u'confidence': 0.585,
                u'intent': u'shopping_newlist'},
            'type': u'chat'}
        ret = test(jsonInput)
        try :
            assert (ret['test'] == 'no-name')    
        except AssertionError :
            print ret["body"]
            raise AssertionError
            
    def test_1getlist(self):
        test=Shopping().getlist
        jsonInput = {'from': u'Lisa-Web', 'zone': u'WebSocket', u'msg_id': u'c7e169a5-9d87-4a43-8a11-9fa75fd0e5ae',
        u'msg_body': u'which list have I',
        u'outcome': {
            u'entities': {
            u'confidence': 0.999,
            u'intent': u'shopping_getlist'},
        'type': u'chat'}}
        ret = test(jsonInput)
        try :
            assert (ret['test'] == 'no-existing')    
        except AssertionError :
            print ret['test']
            print ret["body"]
            raise AssertionError
    
    def test_1getNoExistingList(self):
        test=Shopping().getlist
        jsonInput = {'from': u'Lisa-Web', 'zone': u'WebSocket', u'msg_id': u'c7e169a5-9d87-4a43-8a11-9fa75fd0e5ae',
        u'msg_body': u'which list have I',
        u'outcome': {
            u'entities': {
                u'message_subject': {u'body': u'where ?', u'start': 40, u'end': 60, u'suggested': True, u'value': u'testfoo'},
            u'confidence': 0.999,
            u'intent': u'shopping_getlist'},
        'type': u'chat'}}
        ret = test(jsonInput)
        try :
            assert (ret['test'] == 'no-existing')    
        except AssertionError :
            print ret['test']
            print ret["body"]
            raise AssertionError

    def test_2addItem(self):
        test=Shopping().add
        jsonInput = {'from': u'Lisa-Web', 'zone': u'WebSocket', u'msg_id': u'97c99d41-37d9-4811-95e0-6a5c89d7e1ad',
            u'msg_body': u'add an item for test',
            u'outcome': {
                u'entities': {
                    u'shopping_item': {u'body': u'what ?', u'start': 12, u'end': 24, u'suggested': True, u'value': u'item'},
                    u'number': {u'body': u'how ?', u'start': 8, u'end': 11, u'value': 2},
                    u'message_subject': {u'body': u'where ?', u'start': 40, u'end': 60, u'suggested': True, u'value': u'test'}
                    },
                u'confidence': 0.963,
                u'intent': u'shopping_add'
                },
            'type': u'chat'}
        ret = test(jsonInput)
        try :
            assert (ret['test'] == 'add')    
        except AssertionError :
            print ret["body"]
            raise AssertionError

    def test_2addNoItem(self):
        test=Shopping().add
        jsonInput = {'from': u'Lisa-Web', 'zone': u'WebSocket', u'msg_id': u'97c99d41-37d9-4811-95e0-6a5c89d7e1ad',
            u'msg_body': u'add an item for test',
            u'outcome': {
                u'entities': {
                    u'message_subject': {u'body': u'where ?', u'start': 40, u'end': 60, u'suggested': True, u'value': u'test'}
                    },
                u'confidence': 0.963,
                u'intent': u'shopping_add'
                },
            'type': u'chat'}
        ret = test(jsonInput)
        try :
            assert (ret['test'] == 'no-item')    
        except AssertionError :
            print ret["body"]
            raise AssertionError

    
    def test_2addNoList(self):
        test=Shopping().add
        jsonInput = {'from': u'Lisa-Web', 'zone': u'WebSocket', u'msg_id': u'97c99d41-37d9-4811-95e0-6a5c89d7e1ad',
            u'msg_body': u'add an item for test',
            u'outcome': {
                u'entities': {
                    u'shopping_item': {u'body': u'what ?', u'start': 12, u'end': 24, u'suggested': True, u'value': u'item'},
                    u'number': {u'body': u'how ?', u'start': 8, u'end': 11, u'value': 2}
                    },
                u'confidence': 0.963,
                u'intent': u'shopping_add'
                },
            'type': u'chat'}
        ret = test(jsonInput)
        try :
            assert (ret['test'] == 'no-list')    
        except AssertionError :
            print ret["body"]
            raise AssertionError
            

    def test_3getItem(self):
        test=Shopping().getlist
        jsonInput = {'from': u'Lisa-Web', 'zone': u'WebSocket', u'msg_id': u'97c99d41-37d9-4811-95e0-6a5c89d7e1ad',
            u'msg_body': u'add an item for test',
            u'outcome': {
                u'entities': {
                    u'message_subject': {u'body': u'where ?', u'start': 40, u'end': 60, u'suggested': True, u'value': u'test'}
                    },
                u'confidence': 0.963,
                u'intent': u'shopping_add'
                },
            'type': u'chat'}
        ret = test(jsonInput)
        try :
            assert ('2 item' in ret['test'])    
        except AssertionError :
            print ret["body"]
            raise AssertionError
    
    def test_4deleteNoList(self):
        test=Shopping().deletelist
        jsonInput = {'from': u'Lisa-Web', 'zone': u'WebSocket', u'msg_id': u'97c99d41-37d9-4811-95e0-6a5c89d7e1ad',
            u'msg_body': u'add an item for test',
            u'outcome': {
                u'entities': {
                    },
                u'confidence': 0.963,
                u'intent': u'shopping_add'
                },
            'type': u'chat'}
        ret = test(jsonInput)
        try :
            assert (ret['test'] == 'no-namelist')   
        except AssertionError :
            print ret["body"]
            raise AssertionError
    
    
    def test_4deleteList(self):
        test=Shopping().deletelist
        jsonInput = {'from': u'Lisa-Web', 'zone': u'WebSocket', u'msg_id': u'97c99d41-37d9-4811-95e0-6a5c89d7e1ad',
            u'msg_body': u'add an item for test',
            u'outcome': {
                u'entities': {
                    u'message_subject': {u'body': u'where ?', u'start': 40, u'end': 60, u'suggested': True, u'value': u'test'}
                    },
                u'confidence': 0.963,
                u'intent': u'shopping_add'
                },
            'type': u'chat'}
        ret = test(jsonInput)
        try :
            assert (ret['test'] == 'del-list')   
        except AssertionError :
            print ret["body"]
            raise AssertionError
    
    def test_4deleteNoExisitingList(self):
        test=Shopping().deletelist
        jsonInput = {'from': u'Lisa-Web', 'zone': u'WebSocket', u'msg_id': u'97c99d41-37d9-4811-95e0-6a5c89d7e1ad',
            u'msg_body': u'add an item for test',
            u'outcome': {
                u'entities': {
                    u'message_subject': {u'body': u'where ?', u'start': 40, u'end': 60, u'suggested': True, u'value': u'test'}
                    },
                u'confidence': 0.963,
                u'intent': u'shopping_add'
                },
            'type': u'chat'}
        ret = test(jsonInput)
        try :
            assert (ret['test'] == 'no-existing')   
        except AssertionError :
            print ret["body"]
            raise AssertionError
    
            
# Ceci lance le test si on exécute le script
# directement.
if __name__ == '__main__':
    debug = 0
    if debug == 0 :
        unittest.main(verbosity=2)   #change verbosity here
    else :
    #debug
        pass
