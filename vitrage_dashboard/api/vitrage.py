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
from openstack_dashboard.api import base
from vitrageclient import client as vitrage_client
from contrib import action_manager

import ConfigParser
import logging
LOG = logging.getLogger(__name__)


@memoized
def vitrageclient(request, password=None):
    # endpoint = base.url_for(request, 'identity')
    # token_id = request.user.token.id
    # tenant_name = request.user.tenant_name
    # project_domain_id = request.user.token.project.get('domain_id', 'Default')
    # auth = Token(auth_url=endpoint, token=token_id,
    #              project_name=tenant_name,
    #              project_domain_id=project_domain_id)

    authlist = []
    sessionlist = []
    clientlist = []


    auth1 = Token(auth_url=unicode('http://192.168.11.11/identity'),
                  token=unicode('gAAAAABbofETUf1zFWRqv7RI3jD0k40LwnCu_rpQCYQ6lvVNf1W-AFLHXC_wet0tCrQSyXshKBug5JhL3DU7omoM70Ci5SnvkEGMclwu_CueooCgaq0xBZ4s43sxqwZPLxYYz22_KvEo4iYPchZna-OV1ZQtUzDZ_UB9KEJir98cX9CpDUUy-Y0'),
                 project_name=unicode('admin'),
                 project_domain_id=unicode('default'))
    auth2 = Token(auth_url=unicode('http://192.168.11.101/identity'), token=unicode(
        'gAAAAABbofEc1hPz0el-ZQzCac2thdT5Ln81OO0XT1Rclcr9DRKRBIOgI36Iq07buDNCuPwIzVG9LvnNGXfLL8i3pkCvdfv8w14905cqnRDFkc_C2EeRQt6gwmpiiLJFOhfwI-9FZf_3mdWIn9HIWwVCmPKGC3-Dr9-GkVJ3du0rA3dAsoGhHv8'),
                 project_name=unicode('admin'),
                 project_domain_id=unicode('default'))
    auth3 = Token(auth_url=unicode('http://192.168.11.201/identity'), token=unicode(
        'gAAAAABbofEn1bsjmxnuC3DJL9uXqyWlXBscq8FbzTUwKroPRCQjFCbHXVUp7UN-XxGPWXV2iHPUqvtvxicXwZ_fifDOZNhDEyrPt6B7NircJeOPobO6r0gixYcRTQwEFwLWPfx_TcLJJm5ZRyRtqf9FGVjdddClTgomb4mPpCCnTm3Mj6Eszx0'),
                 project_name=unicode('admin'),
                 project_domain_id=unicode('default'))

    authlist.append(auth1)
    authlist.append(auth2)
    authlist.append(auth3)


    session1 = Session(auth=authlist[0], timeout=600)
    session2 = Session(auth=authlist[1], timeout=600)
    session3 = Session(auth=authlist[2], timeout=600)

    sessionlist.append(session1)
    sessionlist.append(session2)
    sessionlist.append(session3)

    clientlist.append(vitrage_client.Client('1', sessionlist[0]))
    clientlist.append(vitrage_client.Client('1', sessionlist[1]))
    clientlist.append(vitrage_client.Client('1', sessionlist[2]))



    return clientlist


def topology(request, query=None, graph_type='tree', all_tenants='false',
             root=None, limit=None):
    LOG.info("--------- CALLING VITRAGE_CLIENT ---request %s", str(request))
    LOG.info("--------- CALLING VITRAGE_CLIENT ---query %s", str(query))
    LOG.info("------ CALLING VITRAGE_CLIENT --graph_type %s", str(graph_type))
    LOG.info("---- CALLING VITRAGE_CLIENT --all_tenants %s", str(all_tenants))
    LOG.info("--------- CALLING VITRAGE_CLIENT --------root %s", str(root))
    LOG.info("--------- CALLING VITRAGE_CLIENT --------limit %s", str(limit))

    xlist = []
    x1 = vitrageclient(request)

    tmpx0=x1[0].topology.get(query=query,
                       graph_type=graph_type,
                       all_tenants=all_tenants,
                       root=root,
                       limit=limit)

    tmpx1 = x1[1].topology.get(query=query,
                               graph_type=graph_type,
                               all_tenants=all_tenants,
                               root=root,
                               limit=limit)

    tmpx2 = x1[2].topology.get(query=query,
                               graph_type=graph_type,
                               all_tenants=all_tenants,
                               root=root,
                               limit=limit)

    cluster_index = 0
    max_num =0

#### GET cluster index
    for i in tmpx0['nodes'] :
        global cluster_index
        if i['id'] == 'OpenStack Cluster' :
            cluster_index = i['graph_index']

#### GET MAX NUM
    for i in tmpx0['nodes']:
        global max_num
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
    max_num += cnt
    tmpx2_cluster = 0
    for i in tmpx2['nodes']:
        global tmpx2_cluster
        if i['id'] == 'OpenStack Cluster':
            tmpx2_cluster = i['graph_index']

    tmpx2_list = []
    for i in tmpx2['nodes'] :
        global tmpx2_list,tmpx2_cluster
        if i['graph_index'] > tmpx2_cluster:
            tmpx2_list.append(i)


    for j in range(len(tmpx2['links'])):
        tmpx2['links'][j]['s_cha'] = True
        tmpx2['links'][j]['t_cha'] = True

    for i in tmpx2['nodes']:
        global max_num,cluster_index,cnt,tmpx2_list
        if i['id'] != 'OpenStack Cluster' :
            cnt+=1

        for j in range(len(tmpx2['links'])):

            if tmpx2['links'][j]['source'] == i['graph_index'] and i['id'] != 'OpenStack Cluster' and tmpx2['links'][j]['s_cha'] == True:
                if  i not in tmpx2_list:
                    tmpx2['links'][j]['source'] += max_num
                    tmpx2['links'][j]['s_cha'] = False
                else:
                    tmpx2['links'][j]['source'] += (max_num -1)
                    tmpx2['links'][j]['s_cha'] = False

            elif tmpx2['links'][j]['source'] == i['graph_index'] and i['id'] == 'OpenStack Cluster' and tmpx2['links'][j]['s_cha'] == True:
                tmpx2['links'][j]['source'] = cluster_index
                tmpx2['links'][j]['s_cha'] = False


            if tmpx2['links'][j]['target'] == i['graph_index'] and i['id'] != 'OpenStack Cluster' and tmpx2['links'][j]['t_cha'] == True:
                if  i not in tmpx2_list:
                    tmpx2['links'][j]['target'] += max_num
                    tmpx2['links'][j]['t_cha'] = False
                else:
                    tmpx2['links'][j]['target'] += (max_num -1)
                    tmpx2['links'][j]['t_cha'] = False
            elif tmpx2['links'][j]['target'] == i['graph_index'] and i['id'] == 'OpenStack Cluster'and tmpx2['links'][j]['t_cha'] == True:
                tmpx2['links'][j]['target'] = cluster_index
                tmpx2['links'][j]['t_cha'] = False

        if i not in tmpx2_list:
            i['graph_index'] += max_num
        else:
            i['graph_index'] += (max_num - 1)

        if i['id'] == 'nova' :
            i['name'] = 'MEC2_nova'
            i['id'] = 'MEC2_nova'

        if i['id'] != 'OpenStack Cluster':
            tmpx0['nodes'].append(i)

    for i in tmpx2['nodes']:
        global tmpx2_list

        if i not in tmpx2_list:
            i['graph_index'] += max_num
        else:
            i['graph_index'] += (max_num - 1)

        if i['id'] == 'nova':
            i['name'] = 'MEC1_nova'
            i['id'] = 'MEC1_nova'
        if i['id'] != 'OpenStack Cluster':
            tmpx0['nodes'].append(i)

    for j in range(len(tmpx2['links'])):
        del tmpx2['links'][j]['s_cha']
        del tmpx2['links'][j]['t_cha']

    for j in range(len(tmpx2['links'])):
        tmpx0['links'].append(tmpx2['links'][j])

    print(" RESPONSE ",tmpx0)
    print(" RESPONSE ", tmpx0)
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
    print("############################################ request",request)
    print("############################################ aciotn", action)
    print("############################################ requestdict", requestdict)
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



