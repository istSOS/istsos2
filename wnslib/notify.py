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
    """Notify class

    send notifcation via email or twitter
    """

    def __init__(self, serviceconfig):
        self.serviceconfig = serviceconfig
        twitter_conf = self.serviceconfig.twitter
        if twitter_conf['consumer_key']:
            self.twitter_api = twitter.Api(
                            consumer_key=twitter_conf['consumer_key'],
                            consumer_secret=twitter_conf['consumer_secret'],
                            access_token_key=twitter_conf['oauth_token'],
                            access_token_secret=twitter_conf['oauth_secret'])
        else:
            self.twitter_api = None

    def alert(self, message, name):
        """
            alert notification with popup

            Args:
                message (str): message to notify
                name (str): notification name
        """
        # this is blocking
        #TODO: find a non blocking solution. Thread?
        from easygui import msgbox
        msgbox(message, title="Notification from " + name)

    def email(self, message, to):
        """
        Send notification via mail

        Args:
            message (dict): dict with object and mail message

            to (str): mail where to send notification
        """

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
        smtp_server = self.serviceconfig.mail['smtp']
        port = self.serviceconfig.mail['port']

        msg = MIMEMultipart('alternative')
        msg['Subject'] = message['subject']
        msg['From'] = mail_usr
        msg['To'] = to

        part = MIMEText(message['message'], 'plain')
        msg.attach(part)
        try:
            mailServer = smtplib.SMTP(smtp_server, port)
            mailServer.ehlo()
            mailServer.starttls()
            mailServer.ehlo()
            mailServer.login(mail_usr, mail_pwd)
            mailServer.sendmail(mail_usr, to, msg.as_string())
            mailServer.quit()
            print 'successfully sent the mail'
        except Exception as e:
            print 'failed to send mail'
            print e

    def post_twitter_status(self, message, name):
        """Update status twitter

        Args:
            message (str): tweet to send (remember max 140 char)
            name (str): name of the notification (to create hashtag)
        """

        if not self.twitter_api:
            print "please define a twitter account to update status"

        print 'update twitter status'
        tweet = '#' + name + ' '
        tweet += message

        if len(message) < 140:
            try:
                self.twitter_api.PostUpdate(tweet)
            except twitter.TwitterError, e:
                if e[0][0]['code'] == 187:
                    print 'Duplicate tweet'
                else:
                    print e
            except AttributeError as e:
                print e
        else:
            raise Exception("Message for twitter to long!!!, MAX 140 character")

    def twitter(self, message, to, name):
        """
        Send a Twitter private message

        Args:
            message (str): tweet to send (remember max 140 char)
            to (str): user twitter_id to send
            name (str):  name of the notification (to create hashtag)
        """

        import json

        if not self.twitter_api:
            print "please define a twitter account to send private message"

        print 'Send via Twitter'
        # Send direct message
        tweet = '#' + name + ' '
        tweet += message

        user = self.twitter_api.getUser(screen_name=to)
        user = json.loads(str(user))

        if len(message) < 140:
            print 'send direct message'
            try:
                self.twitter_api.PostDirectMessage(user_id=user['id'],
                                    text=tweet, screen_name=to)
            except twitter.TwitterError as e:
                if e[0][0]['code'] == 187:
                    print 'Duplicate tweet'
                else:
                    print e
            except AttributeError as e:
                print e
        else:
            raise Exception("Message for twitter to long!!!, MAX 140 character")

    def ftp(self, ftp_params, message):
        import ftplib
        import StringIO

        print "try ftp"

        try:
            ftps = ftplib.FTP(ftp_params['server'])
        except Exception as e:
            print e

        try:
            ftps.login(user=ftp_params['user'], passwd=ftp_params['passwd'])
        except Exception as e:
            print e

        # create temporary file
        mess = StringIO.StringIO(message['message'])
        # FTP requeire a file

        ftps.storlines('STOR %s' % message['filename'], mess)

        mess.close()
        ftps.close()

        print "end ftp"

    def fax(self, message, to, name):
        """
            Not implemented
        """
        print "notify via FAX"

    def sms(self, message, to, name):
        """
            not implemented
        """
        print "notify via SMS"
