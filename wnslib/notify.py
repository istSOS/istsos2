# -*- coding: utf-8 -*-
# ===============================================================================
#
# Authors: Massimiliano Cannata, Milan Antonovic
#
# Copyright (c) 2015 IST-SUPSI (www.supsi.ch/ist)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
#
# ===============================================================================
from lib import twitter


class Notify(object):

    def __init__(self, serviceconfig):
        self.serviceconfig = serviceconfig
        twitter_conf = self.serviceconfig.twitter
        self.twitter_api = twitter.Api(
                            consumer_key=twitter_conf['consumer_key'],
                            consumer_secret=twitter_conf['consumer_secret'],
                            access_token_key=twitter_conf['oauth_token'],
                            access_token_secret=twitter_conf['oauth_secret'])

    def email(self, message, to):
        print 'send mail'

        if not 'subject' in message.keys():
            print "please define a email subject"
            return
        if not 'message' in message.keys():
            print "please define a email text"
            return

        import smtplib
        from email.MIMEMultipart import MIMEMultipart
        from email.MIMEText import MIMEText

        mail_usr = self.serviceconfig.mail['usermail']
        mail_pwd = self.serviceconfig.mail['password']

        msg = MIMEMultipart('alternative')
        msg['Subject'] = message['subject']
        msg['From'] = mail_usr
        msg['To'] = to

        part = MIMEText(message['message'], 'plain')
        msg.attach(part)

        mailServer = smtplib.SMTP("smtp.gmail.com", 587)
        mailServer.ehlo()
        mailServer.starttls()
        mailServer.ehlo()
        mailServer.login(mail_usr, mail_pwd)
        mailServer.sendmail(mail_usr, to, msg.as_string())
        mailServer.quit()

    def post_twitter_status(self, message, name):
        # Update Status
        if not 'public' in message.keys():
            print "please define a twitter public message"
            return

        print 'update twitter status'
        tweet = '#' + name + ' '
        tweet += message['public']

        if len(message) < 140:
            try:
                self.twitter_api.PostUpdate(tweet)
            except twitter.TwitterError, e:
                if e[0][0]['code'] == 187:
                    print 'Duplicate tweet'
                else:
                    print e
        else:
            raise Exception("Message for twitter to long!!!, MAX 140 character")

    def twitter(self, message, to, name=None):
        if not 'private' in message.keys():
            print "please define a twitter public message"
            return
        print 'Send via Twitter'
        # Send direct message
        tweet = '#' + name + ' '
        tweet += message['private']

        if len(message) < 140:
            print 'send direct message'
            try:
                self.twitter_api.PostDirectMessage(tweet, to, name)
            except twitter.TwitterError, e:
                if e[0][0]['code'] == 187:
                    print 'Duplicate tweet'
                else:
                    print e
        else:
            raise Exception("Message for twitter to long!!!, MAX 140 character")

    def fax(self, message, to, name):
        print "notify via FAX"

    def sms(self, message, to, name):
        print "notify via SMS"