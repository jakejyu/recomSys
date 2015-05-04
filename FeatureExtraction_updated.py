import httplib2
# import urllib2
from urllib.request import urlopen
import glob
import json
import datetime
import statistics
import sys
import time
import os


def getMembers(groupId, timeStamp):
    try:
        members = json.loads(open('members_updated\\' + str(groupId) + '.json').read())
    except:
        print("error crawling member:" + str(groupId))
        members = []
    members = [member for member in members if member['joined'] < timeStamp]
    return members


def getEvents(groupId, timeStamp):
    try:
        events = json.loads(open('events_updated\\' + str(groupId) + '.json').read())
    except:
        print("error crawling event:" + str(groupId))
        events = []
    events = [event for event in events if event['time'] < timeStamp]
    return events


def getGroup(groupID):
    url = "https://api.meetup.com/2/groups?photo-host=public&key=645b491c6e273a7d412a554e676a6f&group_id=" + str(
        groupID) + "&sign=true"
    try:
        # result = urllib2.urlopen(url)
        result = urlopen(url)
    except:
        time.sleep(5)
        # result = urllib2.urlopen(url)
        result = urlopen(url)
    data = json.load(result)
    if len(data['results']) > 0:
        return data['results'][0]
    else:
        return ''


def getAllGroups():
    json_data = open('allGroups.json').read()
    data = json.loads(json_data)
    return data


def getGroupByID(allGroups, groupID):
    for x in allGroups:
        print(str(x))
    group = [x for x in allGroups if x['id'] == groupID]
    if len(group) > 0:
        return group[0]
    else:
        print("can't find group:" + str(groupID))
        return ''



timeSpan = sys.argv[1]
survive = int(sys.argv[2])
if survive == 1:
    lines = open('surviveGroups.txt', 'r').readlines()
else:
    lines = open('deathGroups.txt', 'r').readlines()
allGroups = getAllGroups()

# for i in range(len(lines) / 3):
for i in range(int(len(lines) / 3)):
    # groupId = 2233
    groupId = lines[i * 3].strip('\n')
    timeStamp = lines[i * 3 + 1]
    dt = timeStamp.strip('\n').split('-')
    initialTimeStamp = (datetime.datetime(int(dt[0]), int(dt[1]), int(dt[2])) - datetime.datetime(1970, 1, 1)).total_seconds()
    print(initialTimeStamp)
    timeStamp = initialTimeStamp * 1000 - int(timeSpan) * 30 * 24 * 3600 * 1000

    members = getMembers(groupId, timeStamp)
    events = getEvents(groupId, timeStamp)

    group = getGroupByID(allGroups, int(groupId))
    if len(events) > 0 and group != '':
        avgEvents = sum(event['yes_rsvp_count'] for event in events) / (len(events) * 1.0)
        avgEventsHeadcount = sum(event['headcount'] for event in events) / (len(events) * 1.0)

        if len(members) > 0:
            avgMembers = sum(event['yes_rsvp_count'] for event in events) / (len(members) * 1.0)
        else:
            avgMembers = 0
        eventParticipation = [event['yes_rsvp_count'] for event in events]
        eventHeadCount = [event['headcount'] for event in events]
        if len(events) > 1:
            stdEvent = statistics.stdev(eventParticipation)
            stdEventHeadCount = statistics.stdev(eventHeadCount)
        else:
            stdEvent = 0
            stdEventHeadCount = 0
        eventGap = (timeStamp / 1000.0 - group['created'] / 1000.0) / (len(events) * 1.0)
        eventsWithLimit = []
        eventsWithFee = []
        eventsWithDuration = []
        memberEventCount = {}
        eventOrganizer = []
        memberEvent = {}
        for event in events:
            if 'rsvp_limit' in event:
                eventsWithLimit.append(event)
            if 'fee' in event:
                eventsWithFee.append(event)
            if 'duration' in event:
                eventsWithDuration.append(event)
            try:
                rsvps = json.loads(open('rsvps\\' + str(event['id']) + '.json').read())
            except:
                print("can't crawl event rsvps for event:" + str(event['id']))
                rsvps = []
            rsvpMembers = []

            for rsvp in rsvps:
                if rsvp['response'] == 'yes':
                    rsvpMembers.append(rsvp['member']['member_id'])
                    if memberEventCount.has_key(rsvp['member']['member_id']):
                        memberEventCount[rsvp['member']['member_id']] += 1
                        memberEvent[rsvp['member']['member_id']].append(event['id'])
                    else:
                        memberEventCount[rsvp['member']['member_id']] = 1
                        memberEvent[rsvp['member']['member_id']] = [event['id']]
            listToWrite = []
            for i in range(len(members)):
                if members[i]['id'] in rsvpMembers:
                    listToWrite.append(1)
                else:
                    listToWrite.append(0)
            if survive == 1:
                u = open(
                    'dataAnalysis\\groupEventMember_new\\' + str(sys.argv[1]) + '_positive\\' + str(groupId) + '.txt',
                    'a')
            else:
                u = open(
                    'dataAnalysis\\groupEventMember_new\\' + str(sys.argv[1]) + '_negative\\' + str(groupId) + '.txt',
                    'a')
            u.write(' '.join(map(str, listToWrite)))
            u.write('\n')
            u.close()


            if survive == 1:
                v = open('dataAnalysis\\groupEventMemberSequence_new\\' + str(sys.argv[1]) + '_positive\\' + str(
                    groupId) + '.txt', 'a')
            else:
                v = open('dataAnalysis\\groupEventMemberSequence_new\\' + str(sys.argv[1]) + '_negative\\' + str(
                    groupId) + '.txt', 'a')
            v.write(str(event['id']) + ' ' + datetime.datetime.fromtimestamp(event['time'] / 1000.0).strftime(
                '%Y-%m-%d') + '\n')
            v.close()

            # to record the event id (rows) in the groupEventMember matrix, groupEventMemberSequence

            # to record the user id (colums) in the groupEventMember matrix, write down rsvp['member']['member_id']
            # add record the user id, rsvp['member']['member_id']
            if survive == 1:
                v = open('dataAnalysis\\groupEventMemberSequence_new\\' + str(sys.argv[1]) + '\\' + str(
                    groupId) + '.txt', 'a')
            else:
                v = open('dataAnalysis\\groupEventMemberUserIdSequence\\' + str(sys.argv[1]) + '\\' + str(
                    groupId) + '.txt', 'a')
            v.write(str(rsvp['member']['member_id']) + ' ' + datetime.datetime.fromtimestamp(event['time'] / 1000.0).strftime(
                '%Y-%m-%d') + '\n')
            v.close()



        keys = memberEvent.keys()
        for i in range(len(memberEvent)):
            listToWrite = []
            for j in range(len(memberEvent)):
                listToWrite.append(len(list(set(memberEvent[keys[i]]) & set(memberEvent[keys[j]]))))
            if survive == 1:
                u = open(
                    'dataAnalysis\\groupMemberMatrix_new\\' + str(sys.argv[1]) + '_positive\\' + str(groupId) + '.txt',
                    'a')
            else:
                u = open(
                    'dataAnalysis\\groupMemberMatrix_new\\' + str(sys.argv[1]) + '_negative\\' + str(groupId) + '.txt',
                    'a')
            u.write(' '.join(map(str, listToWrite)))
            u.write('\n')
            u.close()
        activeMembers = len(memberEventCount)
        for member in members:
            if not memberEventCount.has_key(member['id']):
                memberEventCount[member['id']] = 0
        if len(eventsWithLimit) > 0:
            avgEventLimit = sum(event['rsvp_limit'] for event in eventsWithLimit) / (len(eventsWithLimit) * 1.0)
        else:
            avgEventLimit = 0
        if len(eventsWithLimit) > 1:
            stdEventLimit = statistics.stdev([event['rsvp_limit'] for event in eventsWithLimit])
        else:
            stdEventLimit = 0
        if len(eventsWithFee) > 0:
            avgEventFee = sum(event['fee']['amount'] for event in eventsWithFee) / (len(eventsWithFee) * 1.0)
        else:
            avgEventFee = 0
        if len(eventsWithFee) > 1:
            stdEventFee = statistics.stdev([event['fee']['amount'] for event in eventsWithFee])
        else:
            stdEventFee = 0
        if len(eventsWithDuration) > 0:
            avgEventDuration = sum(event['duration'] / 1000.0 for event in eventsWithDuration) / (
            len(eventsWithDuration) * 1.0)
        else:
            avgEventDuration = 0
        if len(eventsWithDuration) > 1:
            stdEventDuration = statistics.stdev([event['duration'] / 1000.0 for event in eventsWithDuration])
        else:
            stdEventDuration = 0
        eventWithFeeRatio = len(eventsWithFee) / (len(events) * 1.0)
        if len(memberEventCount) > 1:
            stdEventAttendance = statistics.stdev(memberEventCount.values())
        else:
            stdEventAttendance = 0
    else:
        avgEvents = 0
        avgMembers = 0
        stdEvent = 0
        eventGap = 0
        avgEventsHeadcount = 0
        stdEventHeadCount = 0
        avgEventLimit = 0
        stdEventLimit = 0
        avgEventFee = 0
        stdEventFee = 0
        avgEventDuration = 0
        stdEventDuration = 0
        eventWithFeeRatio = 0
        activeMembers = 0
        stdEventAttendance = 0

    if len(members) > 0:
        avgJoinTime = sum(member['joined'] / 1000.0 for member in members) / (len(members) * 1.0)
    else:
        avgJoinTime = 0
    if len(members) > 1:
        stdJoinTime = statistics.stdev([member['joined'] / 1000.0 for member in members])
    else:
        stdJoinTime = 0

    eventNum = len(events)
    memberNum = len(members)
    groupLength = timeStamp / 1000.0 - group['created'] / 1000.0
    groupCategory = group['category']['id']
    groupJoinMode = group['join_mode']
    groupVisibility = group['visibility']

    try:
        categoryId = group['category']['id']
    except:
        categoryId = 0
    if survive == 1:
        f = open('dataAnalysis\\groupFeatures_new\\' + str(sys.argv[1]) + '_positive.txt', 'a')
    else:
        f = open('dataAnalysis\\groupFeatures_new\\' + str(sys.argv[1]) + '_negative.txt', 'a')
    f.write(str(group['id']) + ' ' + str(avgEventsHeadcount) + ' ' + str(stdEventHeadCount) + ' ' + str(
        avgEvents) + ' ' + str(stdEvent) + ' ' + str(avgEventLimit) + ' ' + str(stdEventLimit)
            + ' ' + str(avgEventFee) + ' ' + str(stdEventFee) + ' ' + str(avgEventDuration) + ' ' + str(
        stdEventDuration) + ' ' + str(eventWithFeeRatio) + ' ' + str(avgMembers) + ' ' +
            str(stdEventAttendance) + ' ' + str(avgJoinTime) + ' ' + str(stdJoinTime) + ' ' + str(eventGap) + ' ' + str(
        memberNum) + ' ' + str(activeMembers) + ' ' + str(eventNum) + ' '
            + str(groupLength) + ' ' + str(groupCategory) + ' ' + str(groupJoinMode) + ' ' + str(
        groupVisibility) + '\n')
    f.close()
