import re
import os
import imaplib
import time
import urllib2

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
execfile(os.path.join(THIS_DIR, 'version.py'))

__version__ = VERSION


class ImapLibrary(object):

    ROBOT_LIBRARY_VERSION = VERSION
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    port = 993

    def open_mailbox(self, server, user, password):
        """
        Open the mailbox on a mail server with a valid
        authentication.
        """
        self.imap = imaplib.IMAP4_SSL(server, self.port)
        self.imap.login(user, password)
        self.imap.select()

    def wait_for_mail(self, fromEmail, toEmail, timeout=60):
        """
        Wait for an incoming mail from a specific sender to
        a specific mail receiver. Check the mailbox every 10
        seconds for incoming mails until the timeout is exceeded.
        Returns the mail number of the latest email received.

        `timeout` sets the maximum waiting time until an error
        is raised.
        """
        self.fromEmail = fromEmail
        self.toEmail = toEmail
        timeout = int(timeout)
        while (timeout > 0):
            self.imap.recent()
            self.mails = self._check_emails()
            if len(self.mails) > 0:
                return self.mails[-1]
            timeout -= 10
            if timeout > 0:
                time.sleep(10)
        raise AssertionError("No mail received within time")

    def open_link_from_mail(self, mailNumber, linkNumber=0):
        """
        Find a link in an email body and open the link.
        Returns the link's html.

        `linkNumber` declares which link shall be opened (link
        index in body text)
        """
        body = self.imap.fetch(mailNumber, '(BODY[TEXT])')[1][0][1].decode('quoted-printable')
        urls = re.findall(r'href=[\'"]?([^\'" >]+)', body)
        if len(urls) > linkNumber:
            return urllib2.urlopen(urls[linkNumber]).read()
        else:
            raise AssertionError("Link number %i not found!" % linkNumber)

    def close_mailbox(self):
        """
        Close the mailbox after finishing all mail activities of a user.
        """
        self.imap.close()

    def _check_emails(self):
        type, msgnums = self.imap.search(None,
                                         'FROM', self.fromEmail,
                                         'TO', self.toEmail)
        return msgnums[0].split()
