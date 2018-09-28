# Copyright 2015 - Alcatel-Lucent
#
# Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

"""
https://docs.openstack.org/horizon/latest/contributor/tutorials/plugin.html
"""

""" This file will likely be necessary if creating a Django or Angular driven
    plugin. This file is intended to act as a convenient location for
    interacting with the new service this plugin is supporting.
    While interactions with the service can be handled in the views.py,
    isolating the logic is an established pattern in Horizon.
"""

from horizon.utils.memoized import memoized  # noqa
from keystoneauth1.identity.generic.token import Token
from keystoneauth1.session import Session
from keystoneauth1.identity import v3
from openstack_dashboard.api import base
from vitrageclient import client as vitrage_client
from contrib import action_manager

import ConfigParser
import logging
LOG = logging.getLogger(__name__)


@memoized
def vitrageclient(request, password=None):
    endpoint = base.url_for(request, 'identity')
    token_id = request.user.token.id
    tenant_name = request.user.tenant_name
    project_domain_id = request.user.token.project.get('domain_id', 'Default')
    auth = Token(auth_url=endpoint, token=token_id,
                 project_name=tenant_name,
                 project_domain_id=project_domain_id)
    session = Session(auth=auth, timeout=600)
    return vitrage_client.Client('1', session)

def mec_client(request):
    clientlist = []
    meclist = []

    setting = ConfigParser.ConfigParser()
    setting.read('/opt/stack/mecsetting/setting.conf')
    if setting.has_section('Default'):
        if setting.has_option('Default', 'meclist'):
            conf_actions = setting.get('Default', 'meclist').split(',')
            meclist = conf_actions
            for section in conf_actions:
                if setting.has_section(section):
                    option_list = setting.options(section)
                    print(option_list)
                    auth_url = ""
                    user_name = ""
                    password = ""
                    project_name = ""
                    project_domain = ""
                    user_domain = ""

                    for pro in option_list :
                        if 'auth_url' == pro :
                            auth_url = setting.get(section,pro)
                        elif 'user_name' == pro :
                            user_name = setting.get(section,pro)
                        elif 'password' == pro :
                            password = setting.get(section,pro)
                        elif 'project_name' == pro :
                            project_name = setting.get(section,pro)
                        elif 'project_domain_name' == pro :
                            project_domain = setting.get(section,pro)
                        elif 'user_domain_name' == pro :
                            user_domain = setting.get(section,pro)

                    v3_auth = v3.Password(auth_url=auth_url + "/v3",
                                          username=user_name,
                                          password=password,
                                          project_name=project_name,
                                          project_domain_name=project_domain,
                                          user_domain_name=user_domain)

                    v3_ses = Session(auth=v3_auth)
                    auth_token = v3_ses.get_token()

                    auth = Token(auth_url=auth_url,
                                  token=auth_token,
                                  project_name=project_name,
                                  project_domain_id=project_domain)
                    session = Session(auth=auth, timeout=600)
                    clientlist.append(vitrage_client.Client('1', session))


    return clientlist,meclist


def topology(request, query=None, graph_type='tree', all_tenants='false',
             root=None, limit=None):
    LOG.info("--------- CALLING VITRAGE_CLIENT ---request %s", str(request))
    LOG.info("--------- CALLING VITRAGE_CLIENT ---query %s", str(query))
    LOG.info("------ CALLING VITRAGE_CLIENT --graph_type %s", str(graph_type))
    LOG.info("---- CALLING VITRAGE_CLIENT --all_tenants %s", str(all_tenants))
    LOG.info("--------- CALLING VITRAGE_CLIENT --------root %s", str(root))
    LOG.info("--------- CALLING VITRAGE_CLIENT --------limit %s", str(limit))

    mecclient,meclist = mec_client(request)
    tmpx0=mecclient[0].topology.get(query=query,
                       graph_type=graph_type,
                       all_tenants=all_tenants,
                       root=root,
                       limit=limit)

    tmpx1 = mecclient[1].topology.get(query=query,
                               graph_type=graph_type,
                               all_tenants=all_tenants,
                               root=root,
                               limit=limit)

    tmpx2 = mecclient[2].topology.get(query=query,
                               graph_type=graph_type,
                               all_tenants=all_tenants,
                               root=root,
                               limit=limit)

    cluster_index = 0
    max_num =0

    print("##########################################")
    print("tmpx2 ",tmpx2['links'])


#### GET cluster index
    for i in tmpx0['nodes'] :
        global cluster_index
        if i['vitrage_category'] != 'ALARM':
            if i['id'] == 'OpenStack Cluster' :
                cluster_index = i['graph_index']

#### GET MAX NUM
    for i in tmpx0['nodes']:
        global max_num
        if i['vitrage_category'] != 'ALARM':
            if max_num < i['graph_index']:
                max_num = i['graph_index']


####### GET after cluster index

    max_num += 1
    cnt = 0
    tmpx1_cluster = 0
    for i in tmpx1['nodes']:
        global tmpx1_cluster
        if i['id'] == 'OpenStack Cluster':
            tmpx1_cluster = i['graph_index']

    tmpx1_list = []
    for i in tmpx1['nodes'] :
        global tmpx1_list,tmpx1_cluster
        if i['graph_index'] > tmpx1_cluster:
            tmpx1_list.append(i)

    for j in range(len(tmpx1['links'])):
        tmpx1['links'][j]['s_cha'] = True
        tmpx1['links'][j]['t_cha'] = True


    for i in tmpx1['nodes']:
        global max_num,cluster_index,cnt,tmpx1_list
        if i['id'] != 'OpenStack Cluster' :
            cnt+=1

        for j in range(len(tmpx1['links'])):
            if tmpx1['links'][j]['source'] == i['graph_index'] and i['id'] != 'OpenStack Cluster' and \
                            tmpx1['links'][j]['s_cha'] == True:
                if  i in tmpx1_list:
                    tmpx1['links'][j]['source'] += (max_num -1 )
                    tmpx1['links'][j]['s_cha'] = False
                else:
                    tmpx1['links'][j]['source'] += max_num
                    tmpx1['links'][j]['s_cha'] = False

            elif tmpx1['links'][j]['source'] == i['graph_index'] and i['id'] == 'OpenStack Cluster' and \
                            tmpx1['links'][j]['s_cha'] == True:
                tmpx1['links'][j]['source'] = cluster_index
                tmpx1['links'][j]['s_cha'] = False


            if tmpx1['links'][j]['target'] == i['graph_index'] and i['id'] != 'OpenStack Cluster' and \
                            tmpx1['links'][j]['t_cha'] == True:
                if  i in tmpx1_list:
                    tmpx1['links'][j]['target'] += (max_num-1)
                    tmpx1['links'][j]['t_cha'] = False
                else:
                    tmpx1['links'][j]['target'] += max_num
                    tmpx1['links'][j]['t_cha'] = False
            elif tmpx1['links'][j]['target'] == i['graph_index'] and i['id'] == 'OpenStack Cluster' and \
                            tmpx1['links'][j]['t_cha'] == True :
                tmpx1['links'][j]['target'] = cluster_index
                tmpx1['links'][j]['t_cha'] = False




    for i in tmpx1['nodes']:
        global tmpx1_list

        if i not in tmpx1_list:
            i['graph_index'] += max_num
        else:
            i['graph_index'] += (max_num - 1)

        if i['id'] == 'nova':
            i['name'] = 'MEC1_nova'
            i['id'] = 'MEC1_nova'
        if i['id'] != 'OpenStack Cluster':
            tmpx0['nodes'].append(i)

    for j in range(len(tmpx1['links'])):
        del tmpx1['links'][j]['s_cha']
        del tmpx1['links'][j]['t_cha']

    for j in range(len(tmpx1['links'])):
        tmpx0['links'].append(tmpx1['links'][j])

### SET TMPX2 link & nodes
    max_num +=( cnt-1)
    tmpx2_cluster = 0
    for i in tmpx2['nodes']:
        global tmpx2_cluster
        if i['id'] == 'OpenStack Cluster':
            tmpx2_cluster = i['graph_index']

    tmpx2_list = []
    clu=False
    for i in tmpx2['nodes'] :
        global tmpx2_list,tmpx2_cluster,clu

        if i['vitrage_category'] == 'openstack.cluster':
            clu = True
        elif clu == True :
            tmpx2_list.append(i)


    for j in range(len(tmpx2['links'])):
        tmpx2['links'][j]['s_cha'] = True
        tmpx2['links'][j]['t_cha'] = True

    for i in tmpx2['nodes']:
        global max_num,cluster_index,cnt,tmpx2_list,tmpx2_cluster
        for j in range(len(tmpx2['links'])):
            if  tmpx2['links'][j]['source'] == tmpx2_cluster and tmpx2['links'][j]['s_cha'] == True:
                tmpx2['links'][j]['source'] = cluster_index
                tmpx2['links'][j]['s_cha'] = False

            if tmpx2['links'][j]['target'] == tmpx2_cluster and tmpx2['links'][j]['t_cha'] == True:
                    tmpx2['links'][j]['target'] = cluster_index
                    tmpx2['links'][j]['t_cha'] = False
            else:
                if tmpx2['links'][j]['s_cha'] == True:
                    if  i not in tmpx2_list:
                        tmpx2['links'][j]['source'] += max_num
                        tmpx2['links'][j]['s_cha'] = False
                    else:
                        tmpx2['links'][j]['source'] += (max_num -1)
                        tmpx2['links'][j]['s_cha'] = False

                if tmpx2['links'][j]['t_cha'] == True:
                    if  i not in tmpx2_list:
                         tmpx2['links'][j]['target'] += max_num
                         tmpx2['links'][j]['t_cha'] = False
                    else:
                         tmpx2['links'][j]['target'] += (max_num -1)
                         tmpx2['links'][j]['t_cha'] = False


    #
    # for i in tmpx2['nodes']:
    #     global max_num,cluster_index,cnt,tmpx2_list
    #     for j in range(len(tmpx2['links'])):
    #         if i['id'] != 'OpenStack Cluster' and tmpx2['links'][j]['s_cha'] == True:
    #             if i['vitrage_category'] == 'ALARM':
    #                 print("Dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd")
    #             if  i not in tmpx2_list:
    #                 tmpx2['links'][j]['source'] += max_num
    #                 tmpx2['links'][j]['s_cha'] = False
    #             else:
    #                 tmpx2['links'][j]['source'] += (max_num -1)
    #                 tmpx2['links'][j]['s_cha'] = False
    #         elif i['id'] == 'OpenStack Cluster' and tmpx2['links'][j]['s_cha'] == True:
    #             tmpx2['links'][j]['source'] = cluster_index
    #             tmpx2['links'][j]['s_cha'] = False
    #             continue
    #
    #         if i['id'] != 'OpenStack Cluster' and tmpx2['links'][j]['t_cha'] == True:
    #             if  i not in tmpx2_list:
    #                  tmpx2['links'][j]['target'] += max_num
    #                  tmpx2['links'][j]['t_cha'] = False
    #             else:
    #                  tmpx2['links'][j]['target'] += (max_num -1)
    #                  tmpx2['links'][j]['t_cha'] = False
    #         elif i['id'] == 'OpenStack Cluster'and tmpx2['links'][j]['t_cha'] == True:
    #             tmpx2['links'][j]['target'] = cluster_index
    #             tmpx2['links'][j]['t_cha'] = False
    #             if i['vitrage_category'] == 'ALARM':
    #                 print("Dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd")

    # for i in tmpx2['nodes']:
    #     global max_num,cluster_index,cnt,tmpx2_list
    #     if i['vitrage_category'] != 'ALARM' :
    #         for j in range(len(tmpx2['links'])):
    #             if i['vitrage_category'] != 'ALARM':
    #                 if tmpx2['links'][j]['source'] == i['graph_index'] and i['id'] != 'OpenStack Cluster' and tmpx2['links'][j]['s_cha'] == True:
    #                     if  i not in tmpx2_list:
    #                         tmpx2['links'][j]['source'] += max_num
    #                         tmpx2['links'][j]['s_cha'] = False
    #                     else:
    #                         tmpx2['links'][j]['source'] += (max_num -1)
    #                         tmpx2['links'][j]['s_cha'] = False
    #
    #                 elif tmpx2['links'][j]['source'] == i['graph_index'] and i['id'] == 'OpenStack Cluster' and tmpx2['links'][j]['s_cha'] == True:
    #                     tmpx2['links'][j]['source'] = cluster_index
    #                     tmpx2['links'][j]['s_cha'] = False
    #
    #                 if tmpx2['links'][j]['target'] == i['graph_index'] and i['id'] != 'OpenStack Cluster' and tmpx2['links'][j]['t_cha'] == True:
    #                     if  i not in tmpx2_list:
    #                         tmpx2['links'][j]['target'] += max_num
    #                         tmpx2['links'][j]['t_cha'] = False
    #                     else:
    #                         tmpx2['links'][j]['target'] += (max_num -1)
    #                         tmpx2['links'][j]['t_cha'] = False
    #                 elif tmpx2['links'][j]['target'] == i['graph_index'] and i['id'] == 'OpenStack Cluster'and tmpx2['links'][j]['t_cha'] == True:
    #                      tmpx2['links'][j]['target'] = cluster_index
    #                      tmpx2['links'][j]['t_cha'] = False
    #             elif i['vitrage_category'] == 'ALARM' :
    #                 if tmpx2['links'][j]['s_cha'] == True:
    #                     if i not in tmpx2_list:
    #                         tmpx2['links'][j]['source'] += max_num
    #                         tmpx2['links'][j]['s_cha'] = False
    #                     else:
    #                         tmpx2['links'][j]['source'] += (max_num - 1)
    #                         tmpx2['links'][j]['s_cha'] = False
    #
    #                 if tmpx2['links'][j]['t_cha'] == True:
    #                     if i not in tmpx2_list:
    #                         tmpx2['links'][j]['target'] += max_num
    #                         tmpx2['links'][j]['t_cha'] = False
    #                     else:
    #                         tmpx2['links'][j]['target'] += (max_num - 1)
    #                         tmpx2['links'][j]['t_cha'] = False

    for i in tmpx2['nodes']:
        global tmpx2_list
        if i['vitrage_category'] == 'ALARM':
             pass
        elif i['vitrage_category'] != 'ALARM' :
            if i not in tmpx2_list:
                i['graph_index'] += max_num
            else:
                i['graph_index'] += (max_num - 1)

        if i['id'] == 'nova':
            i['name'] = 'MEC2_nova'
            i['id'] = 'MEC2_nova'

        if i['id'] != 'OpenStack Cluster':
            tmpx0['nodes'].append(i)

    for j in range(len(tmpx2['links'])):
        del tmpx2['links'][j]['s_cha']
        del tmpx2['links'][j]['t_cha']

    for j in range(len(tmpx2['links'])):
        tmpx0['links'].append(tmpx2['links'][j])

    max_num = 0
    return tmpx0


def alarms(request, vitrage_id='all', all_tenants='false'):
    return vitrageclient(request).alarm.list(vitrage_id=vitrage_id,
                                             all_tenants=all_tenants)


def alarm_counts(request, all_tenants='false'):
    counts = vitrageclient(request).alarm.count(all_tenants=all_tenants)
    counts['NA'] = counts.get("N/A")
    return counts


def rca(request, alarm_id, all_tenants='false'):
    return vitrageclient(request).rca.get(alarm_id=alarm_id,
                                          all_tenants=all_tenants)


def templates(request, template_id='all'):
    if template_id == 'all':
        return vitrageclient(request).template.list()
    return vitrageclient(request).template.show(template_id)



def actions(request, action, nodetype):
    endpoint = base.url_for(request, 'identity')
    token_id = request.user.token.id
    tenant_name = request.user.tenant_name
    project_domain_id = request.user.token.project.get('domain_id', 'Default')
    auth = Token(auth_url=endpoint, token=token_id,
                 project_name=tenant_name,
                 project_domain_id=project_domain_id)
    session = Session(auth=auth, timeout=600)
    result = action_manager.ActionManager.getinfo(session, str(action),request)
    return result

def action_request(request, action, requestdict):
    endpoint = base.url_for(request, 'identity')
    token_id = request.user.token.id
    tenant_name = request.user.tenant_name
    project_domain_id = request.user.token.project.get('domain_id', 'Default')
    auth = Token(auth_url=endpoint, token=token_id,
                 project_name=tenant_name,
                 project_domain_id=project_domain_id)

    session = Session(auth=auth, timeout=600)
    result = action_manager.ActionManager.execute(session, str(action),requestdict)
    return result

def action_setting(request):
    setting = ConfigParser.ConfigParser()
    setting.read('/etc/vitrage-dashboard/setting.conf')
    actionlist = []
    urllist = {}
    if setting.has_section('Default'):
        if setting.has_option('Default', 'actions'):
            conf_actions = setting.get('Default', 'actions').split(',')

            for section in conf_actions:
                result = None
                if setting.has_section(section):
                    option_list = setting.options(section)
                    matching = [pro for pro in option_list
                                if ('url' in pro)]
                    if matching:
                        urllist[section] = setting.get(section,
                                                           matching[0])
                else:
                    result = action_manager.ActionManager.importcheck(section,request)

                if result:
                    actionlist.append(section.capitalize())
        return [actionlist, urllist]



