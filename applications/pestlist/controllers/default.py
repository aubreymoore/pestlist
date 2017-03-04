# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

# -------------------------------------------------------------------------
# This is a sample controller
# - index is the default action of any application
# - user is required for authentication and authorization
# - download is for downloading files uploaded in the db (does streaming)
# -------------------------------------------------------------------------


def display_taxonomic_tree():
    import json
    # Important: root nodes must have 'parent':'#'
    m = None
    #root_taxon = ''

    form=FORM('Root taxon (leave blank to include all taxa):',
        INPUT(_name='root_taxon'),
        INPUT(_type='submit'),
    )

    if form.accepts(request,session):

        root_taxon = form.vars.root_taxon
        print(root_taxon)

        #level_dict = {'kingdom':1,'phylum':2,'class':3,'order':4,'family':5,'genus':6,'species':7}
        if root_taxon == '':
            rows = db(db.taxon2).select(orderby=db.taxon2.lineage)
        else:
            rows = db(db.taxon2.lineage.contains(root_taxon)).select(orderby=db.taxon2.lineage)
            rows[0].parent_tid = '#'

        mylist = []
        for row in rows:
            if row.trank in ['genus','species']:
                text = '{} <i>{}</i>'.format(row.trank, row.name)
            else:
                text = '{} {}'.format(row.trank, row.name)
            mylist.append({'id':row.tid,'parent':row.parent_tid,'text':text})
        m = json.dumps(mylist)

    elif form.errors:
        response.flash = 'form has errors'
    else:
        response.flash = 'Please select a root taxon and press "SUBMIT QUERY".'
    return dict(form=form, m=m)

# def show_tree():
#     root_taxon = 'Plantae'
#     level_dict = {'kingdom':1,'phylum':2,'class':3,'order':4,'family':5,'genus':6,'species':7}
#     previous_level = 0
#     s = '<ul>\n'
#     first_row = True
#     for row in db(db.taxon2.lineage.contains(root_taxon)).select(orderby=db.taxon2.lineage):
#         if first_row:
#             previous_level = level_dict[row.trank]
#             first_row = False
#         level = level_dict[row.trank]
#         while level > previous_level:
#             s +='<ul>\n'
#             previous_level += 1
#         while level < previous_level:
#             s += '</ul>\n'
#             previous_level -= 1
#         s+= '<li>{} {}</li>\n'.format(row.trank, row.name)
#         previous_level = level
#     return dict(s=s)
#
# def show_tree3():
#     return locals()
#
# def show_tree2():
#     root_taxon = 'Plantae'
#     level_dict = {'kingdom':1,'phylum':2,'class':3,'order':4,'family':5,'genus':6,'species':7}
#     rows = db(db.taxon2.lineage.contains(root_taxon)).select(orderby=db.taxon2.lineage)
#     return locals()
#
#

def get_extracted_names():
    '''
    Returns the contents of the 'extracted_names_json' field in the first
    record of the 'extracted_names' table.
    '''
    return db(db.extracted_names).select()[0]['extracted_names_json']


# def parse_resolved_names():
#     '''
#     docs go Here
#     '''
#     rows = db(db.taxon).select()
#     if len(rows) == 0:
#         db.taxon.insert(name='root', tid=0)
#         print('root added')
#
#     resolved_names_list = get_extracted_names()['resolved_names']
#     for resolved_name in resolved_names_list:
#         results_list = resolved_name.get('results', None)
#         if results_list:
#             result_dict = results_list[0]
#             classification_path = result_dict['classification_path'].split('|')
#             classification_path_ids = result_dict['classification_path_ids'].split('|')
#             classification_path_ranks = result_dict['classification_path_ranks'].split('|')
#
#             print classification_path
#
#             assert classification_path_ranks[0] == 'kingdom'
#             assert len(classification_path) == len(classification_path_ids)
#             assert len(classification_path_ids) == len(classification_path_ranks)
#
#             for i in range(len(classification_path)):
#                 if i == 0:
#                     parent_tid = 0
#                 else:
#                     parent_tid = classification_path_ids[i-1]
#
#                 tid = classification_path_ids[i]
#                 name = classification_path[i]
#                 trank = classification_path_ranks[i]
#
#                 try:
#                     print('trying to add tid={}, name={}, trank={}, parent_tid={}'.format(tid, name, trank, parent_tid))
#                     db.taxon.insert(tid=tid, name=name, trank=trank, parent_tid=parent_tid)
#                     print( '{} added'.format(name))
#                 except sqlite3.IntegrityError:
#                     print('{} not added - already in DB.'.format(name))
#                     pass
#     return

def parse_resolved_names2():
    '''
    Parses the JSON data stored in 'db.extracted_names.extracted_names_json' and
    inserts all taxa to a self-referencing table, 'db.taxon2'. Fields in
    this table are:

        tid: taxon id; usually a GBIF taxon id
        parent_tid: tid of the taxon's parent; parent of a root must be '#'
        name: taxon name
        trank: taxon rank (kingdom, phylum, class, order family, genus or species)
        lineage: ancestors of the taxon; eg. lineage for Oryctes rhinoceros is:
            Animalia|Arthropoda|Insecta|Coleoptera|Dynastidae|Oryctes|Oryctes rhinoceros

    Dependancies:
        get_extracted_names
    '''
    import sqlite3

    resolved_names_list = get_extracted_names()['resolved_names']
    for resolved_name in resolved_names_list:
        results_list = resolved_name.get('results', None)
        if results_list:
            result_dict = results_list[0]
            #lineage = result_dict['classification_path']
            classification_path = result_dict['classification_path'].split('|')
            classification_path_ids = result_dict['classification_path_ids'].split('|')
            classification_path_ranks = result_dict['classification_path_ranks'].split('|')

            print classification_path

            assert classification_path_ranks[0] == 'kingdom'
            assert len(classification_path) == len(classification_path_ids)
            assert len(classification_path_ids) == len(classification_path_ranks)

            for i in range(len(classification_path)):
                if i == 0:
                    parent_tid = '#' # The hash symbol is used by jstree to signify a root node
                else:
                    parent_tid = classification_path_ids[i-1]
                tid = classification_path_ids[i]
                name = classification_path[i]
                trank = classification_path_ranks[i]
                lineage = '|'.join(classification_path[0:i+1])

                try:
                    print('trying to add tid={}, name={}, trank={}, lineage={}'.format(tid, name, trank, lineage))
                    db.taxon2.insert(tid=tid, parent_tid=parent_tid, name=name, trank=trank, lineage=lineage)
                    print( '{} added'.format(name))
                except sqlite3.IntegrityError:
                    print('{} not added - already in DB.'.format(name))
                    pass
    return

#@auth.requires_login()
def show_taxon2():
    grid = SQLFORM.grid(db.taxon2, maxtextlength=1000, paginate=1000)
    return locals()

def find_names(doc_url):
    '''
    Uses the Global Names Resolver to extract scientific names from 'doc_url'
    which can point to an HTML or PDF document.
    '''
    import requests
    import time

    url = 'http://gnrd.globalnames.org/name_finder.json?'
    #params = {'url': 'https://aubreymoore.github.io/crop-pest-list/list.html'}
    params = {'url': doc_url, 'data_source_ids': '11'}
    r = requests.get(url, params)
    mydict = r.json()
    token_url = mydict['token_url']
    print('token_url: {}'.format(token_url))

    # Poll the token url once a second for 100 s to see if results have been returned.
    i = 0
    while i <= 100:
        i += 1
        time.sleep(1)
        r = requests.get(token_url)
        mydict = r.json()
        status = mydict.get('status','')
        queue_size = mydict.get('queue_size','')
        print('{} status: {} queue_size: {}'.format(i, status, queue_size))
        if status != 303:
            break
    return(mydict)


def doit():
    '''
    Uses the find_names function to extract scientific names from
    'https://aubreymoore.github.io/crop-pest-list/list.html' and stores the
    returned JSON data in db.extracted_names.

    Dependancies:
        find_names
    '''
    if len(db(db.extracted_names).select())==0:
        doc_url = 'https://aubreymoore.github.io/crop-pest-list/list.html'
        db.extracted_names.insert(extracted_names_json=find_names(doc_url))
        return('Added record.')
    return('Did not add record')


def index():
    return dict(message=T('Welcome to pestlist!'))


# def user():
#     """
#     exposes:
#     http://..../[app]/default/user/login
#     http://..../[app]/default/user/logout
#     http://..../[app]/default/user/register
#     http://..../[app]/default/user/profile
#     http://..../[app]/default/user/retrieve_password
#     http://..../[app]/default/user/change_password
#     http://..../[app]/default/user/bulk_register
#     use @auth.requires_login()
#         @auth.requires_membership('group name')
#         @auth.requires_permission('read','table name',record_id)
#     to decorate functions that need access control
#     also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
#     """
#     return dict(form=auth())
#
#
# @cache.action()
# def download():
#     """
#     allows downloading of uploaded files
#     http://..../[app]/default/download/[filename]
#     """
#     return response.download(request, db)
#
#
# def call():
#     """
#     exposes services. for example:
#     http://..../[app]/default/call/jsonrpc
#     decorate with @services.jsonrpc the functions to expose
#     supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
#     """
#     return service()
