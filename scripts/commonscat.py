#!/usr/bin/python
# -*- coding: utf-8  -*-
"""
With this tool you can add the template {{commonscat}} to categories.
The tool works by following the interwiki links. If the template is present on
another langauge page, the bot will use it.

You could probably use it at articles as well, but this isn't tested.

This bot uses pagegenerators to get a list of pages. The following options are
supported:

&params;

-always           Don't prompt you for each replacement. Warning message
                  has not to be confirmed. ATTENTION: Use this with care!

-summary:XYZ      Set the action summary message for the edit to XYZ,
                  otherwise it uses messages from add_text.py as default.

-checkcurrent     Work on all category pages that use the primary commonscat
                  template.

For example to go through all categories:
commonscat.py -start:Category:!
"""
"""
Commonscat bot:

Take a page. Follow the interwiki's and look for the commonscat template
*Found zero templates. Done.
*Found one template. Add this template
*Found more templates. Ask the user <- still have to implement this

TODO:
*Update interwiki's at commons
*Collect all possibilities also if local wiki already has link.
*Better support for other templates (translations) / redundant templates.
*Check mode, only check pages which already have the template
*More efficient like interwiki.py
*Possibility to update other languages in the same run
"""

"""
Porting notes:

*Ported from compat to core
*Replaced now-deprecated Page methods
*Fixed way of finding interlanguage links in findCommonscatLink()
*Removed unused and now possibly broken updateInterwiki() method

Ported by Allen Guo <Guoguo12@gmail.com>
November 2013
"""

#
# (C) Multichill, 2008-2009
# (C) Xqt, 2009-2013
# (C) Pywikipedia bot team, 2008-2012
#
# Distributed under the terms of the MIT license.
#
__version__ = '$Id$'
#

import re

import add_text
import pywikibot
from pywikibot import config
from pywikibot import pagegenerators

docuReplacements = {
    '&params;': pagegenerators.parameterHelp
}

# Primary template, list of alternatives
# No entry needed if it is like _default
commonscatTemplates = {
    '_default': (u'Commonscat', []),
    'af': (u'CommonsKategorie', [u'commonscat']),
    'an': (u'Commonscat', [u'Commons cat']),
    'ar': (u'تصنيف كومنز',
           [u'Commonscat', u'تصنيف كومونز', u'Commons cat', u'CommonsCat']),
    'arz': (u'Commons cat', [u'Commoncat']),
    'az': (u'CommonsKat', [u'Commonscat']),
    'bn': (u'কমন্সক্যাট', [u'Commonscat']),
    'ca': (u'Commonscat', [u'Commons cat', u'Commons category']),
    'crh': (u'CommonsKat', [u'Commonscat']),
    'cs': (u'Commonscat', [u'Commons cat']),
    'da': (u'Commonscat',
           [u'Commons cat', u'Commons category', u'Commonscat left',
            u'Commonscat2']),
    'de': (u'Commonscat', [u'Commons cat']),
    'en': (u'Commons category',
           [u'Commoncat', u'Commonscat', u'Commons cat', u'Commons+cat',
            u'Commonscategory', u'Commons and category', u'Commonscat-inline',
            u'Commons category-inline', u'Commons2', u'Commons category multi',
            u'Cms-catlist-up', u'Catlst commons', u'Commonscat show2',
            u'Sister project links']),
    'es': (u'Commonscat',
           [u'Ccat', u'Commons cat', u'Categoría Commons',
            u'Commonscat-inline']),
    'et': (u'Commonsi kategooria',
           [u'Commonscat', u'Commonskat', u'Commons cat', u'Commons category']),
    'eu': (u'Commonskat', [u'Commonscat']),
    'fa': (u'ویکی‌انبار-رده',
           [u'Commonscat', u'Commons cat', u'انبار رده', u'Commons category',
            u'انبار-رده', u'جعبه پیوند به پروژه‌های خواهر',
            u'در پروژه‌های خواهر', u'پروژه‌های خواهر']),
    'fr': (u'Commonscat', [u'CommonsCat', u'Commons cat', u'Commons category']),
    'frp': (u'Commonscat', [u'CommonsCat']),
    'ga': (u'Catcómhaoin', [u'Commonscat']),
    'hi': (u'Commonscat', [u'Commons2', u'Commons cat', u'Commons category']),
    'hu': (u'Commonskat', [u'Közvagyonkat']),
    'hy': (u'Վիքիպահեստ կատեգորիա',
           [u'Commonscat', u'Commons cat', u'Commons category']),
    'id': (u'Commonscat',
           [u'Commons cat', u'Commons2', u'CommonsCat', u'Commons category']),
    'is': (u'CommonsCat', [u'Commonscat']),
    'ja': (u'Commonscat', [u'Commons cat', u'Commons category']),
    'jv': (u'Commonscat', [u'Commons cat']),
    'kaa': (u'Commons cat', [u'Commonscat']),
    'kk': (u'Commonscat', [u'Commons2']),
    'ko': (u'Commonscat', [u'Commons cat', u'공용분류']),
    'la': (u'CommuniaCat', []),
    'mk': (u'Ризница-врска',
           [u'Commonscat', u'Commons cat', u'CommonsCat', u'Commons2',
            u'Commons category']),
    'ml': (u'Commonscat', [u'Commons cat', u'Commons2']),
    'ms': (u'Kategori Commons', [u'Commonscat', u'Commons category']),
    'nn': (u'Commonscat', [u'Commons cat']),
    'os': (u'Commonscat', [u'Commons cat']),
    'pt': (u'Commonscat', [u'Commons cat']),
    'ro': (u'Commonscat', [u'Commons cat']),
    'ru': (u'Commonscat', [u'Викисклад-кат', u'Commons category']),
    'simple': (u'Commonscat',
               [u'Commons cat',  u'Commons cat multi', u'Commons category',
                u'Commons category multi', u'CommonsCompact',
                u'Commons-inline']),
    'sh': (u'Commonscat', [u'Commons cat']),
    'sl': (u'Kategorija v Zbirki',
           [u'Commonscat', u'Kategorija v zbirki', u'Commons cat',
            u'Katzbirke']),
    'sv': (u'Commonscat',
           [u'Commonscat-rad', u'Commonskat', u'Commons cat', u'Commonscatbox',
            u'Commonscat-box']),
    'sw': (u'Commonscat', [u'Commons2', u'Commons cat']),
    'te': (u'Commonscat', [u'Commons cat']),
    'tr': (u'Commons kategori',
           [u'CommonsKat', u'Commonscat', u'Commons cat']),
    'uk': (u'Commonscat', [u'Commons cat', u'Category', u'Commonscat-inline']),
    'vi': (u'Commonscat',
           [u'Commons2', u'Commons cat', u'Commons category', u'Commons+cat']),
    'zh': (u'Commonscat', [u'Commons cat', u'Commons category']),
    'zh-classical': (u'共享類', [u'Commonscat']),
    'zh-yue': (u'同享類',
               [u'Commonscat', u'共享類 ', u'Commons cat', u'Commons category']),
}

ignoreTemplates = {
    'af': [u'commons'],
    'ar': [u'تحويلة تصنيف', u'كومنز', u'كومونز', u'Commons'],
    'be-x-old': [u'Commons', u'Commons category'],
    'cs': [u'Commons', u'Sestřičky', u'Sisterlinks'],
    'da': [u'Commons', u'Commons left', u'Commons2', u'Commonsbilleder',
           u'Commonskat', u'Commonscat2', u'GalleriCommons', u'Søsterlinks'],
    'de': [u'Commons', u'ZhSZV', u'Bauwerk-stil-kategorien',
           u'Bauwerk-funktion-kategorien', u'KsPuB',
           u'Kategoriesystem Augsburg-Infoleiste',
           u'Kategorie Ge', u'Kategorie v. Chr. Ge',
           u'Kategorie Geboren nach Jh. v. Chr.', u'Kategorie Geboren nach Jh.',
           u'!Kategorie Gestorben nach Jh. v. Chr.',
           u'!Kategorie Gestorben nach Jh.',
           u'Kategorie Jahr', u'Kategorie Jahr v. Chr.',
           u'Kategorie Jahrzehnt', u'Kategorie Jahrzehnt v. Chr.',
           u'Kategorie Jahrhundert', u'Kategorie Jahrhundert v. Chr.',
           u'Kategorie Jahrtausend', u'Kategorie Jahrtausend v. Chr.'],
    'en': [u'Category redirect', u'Commons', u'Commonscat1A', u'Commoncats',
           u'Commonscat4Ra',
           u'Sisterlinks', u'Sisterlinkswp', u'Sister project links',
           u'Tracking category', u'Template category', u'Wikipedia category'],
    'eo': [u'Commons',
           (u'Projekto/box', 'commons='),
           (u'Projekto', 'commons='),
           (u'Projektoj', 'commons='),
           (u'Projektoj', 'commonscat=')],
    'es': [u'Commons', u'IprCommonscat'],
    'eu': [u'Commons'],
    'fa': [u'Commons', u'ویکی‌انبار', u'Category redirect', u'رده بهتر',
           u'جعبه پیوند به پروژه‌های خواهر', u'در پروژه‌های خواهر',
           u'پروژه‌های خواهر'],
    'fi': [u'Commonscat-rivi', u'Commons-rivi', u'Commons'],
    'fr': [u'Commons', u'Commons-inline', (u'Autres projets', 'commons=')],
    'fy': [u'Commons', u'CommonsLyts'],
    'hr': [u'Commons', (u'WProjekti', 'commonscat=')],
    'is': [u'Systurverkefni', u'Commons'],
    'it': [(u'Ip', 'commons='), (u'Interprogetto', 'commons=')],
    'ja': [u'CommonscatS', u'SisterlinksN', u'Interwikicat'],
    'ms': [u'Commons', u'Sisterlinks', u'Commons cat show2'],
    'nds-nl': [u'Commons'],
    'nl': [u'Commons', u'Commonsklein', u'Commonscatklein', u'Catbeg',
           u'Catsjab', u'Catwiki'],
    'om': [u'Commons'],
    'pt': [u'Correlatos'],
    'simple': [u'Sisterlinks'],
    'ru': [u'Навигация', u'Навигация для категорий', u'КПР', u'КБР',
           u'Годы в России', u'commonscat-inline'],
    'tt': [u'Навигация'],
    'zh': [u'Category redirect', u'cr', u'Commons',
           u'Sisterlinks', u'Sisterlinkswp',
           u'Tracking category', u'Trackingcatu',
           u'Template category', u'Wikipedia category'
           u'分类重定向', u'追蹤分類', u'共享資源', u'追蹤分類'],
}

msg_change = {
    'be-x-old': u'Робат: зьмяніў шаблён [[:Commons:Category:%(oldcat)s|%(oldcat)s]] на [[:Commons:Category:%(newcat)s|%(newcat)s]]',
    'cs': u'Robot změnil šablonu Commonscat z [[:Commons:Category:%(oldcat)s|%(oldcat)s]] na [[:Commons:Category:%(newcat)s|%(newcat)s]]',
    'da': u'Robot: Ændrer commonscat link fra [[:Commons:Category:%(oldcat)s|%(oldcat)s]] til [[:Commons:Category:%(newcat)s|%(newcat)s]]',
    'de': u'Bot: Ändere commonscat link von [[:Commons:Category:%(oldcat)s|%(oldcat)s]] zu [[:Commons:Category:%(newcat)s|%(newcat)s]]',
    'en': u'Bot: Changing commonscat link from [[:Commons:Category:%(oldcat)s|%(oldcat)s]] to [[:Commons:Category:%(newcat)s|%(newcat)s]]',
    'fa': u'ربات: تغییر پیوند به انبار از [[:Commons:Category:%(oldcat)s|%(oldcat)s]] به [[:Commons:Category:%(newcat)s|%(newcat)s]]',
    'fr': u'Robot: Changé commonscat link de [[:Commons:Category:%(oldcat)s|%(oldcat)s]] à [[:Commons:Category:%(newcat)s|%(newcat)s]]',
    'frr': u'Bot: Feranere commonscat link faan [[:Commons:Category:%(oldcat)s|%(oldcat)s]] tu [[:Commons:Category:%(newcat)s|%(newcat)s]]',
    'is': u'Vélmenni: Breyti Commonscat tengli frá [[:Commons:Category:%(oldcat)s|%(oldcat)s]] í [[:Commons:Category:%(newcat)s|%(newcat)s]]',
    'pdc': u'Waddefresser: commonscat Gleecher vun [[:Commons:Category:%(oldcat)s|%(oldcat)s]] nooch [[:Commons:Category:%(newcat)s|%(newcat)s]] geennert',
    'ru': u'Бот: Изменение commonscat-ссылки с [[:Commons:Category:%(oldcat)s|%(oldcat)s]] на [[:Commons:Category:%(newcat)s|%(newcat)s]]',
    'sk': u'Robot zmenil šablónu Commonscat z [[:Commons:Category:%(oldcat)s|%(oldcat)s]] na [[:Commons:Category:%(newcat)s|%(newcat)s]]',
    'uk': u'Бот: Зміна commonscat-посилання з [[:Commons:Category:%(oldcat)s|%(oldcat)s]] на [[:Commons:Category:%(newcat)s|%(newcat)s]]',
    'th': u'บอต: เปลี่ยนลิงก์หมวดหมู่คอมมอนส์จาก [[:Commons:Category:%(oldcat)s|%(oldcat)s]] เป็น [[:Commons:Category:%(newcat)s|%(newcat)s]]',
    'zh': u'機器人：更改 commonscat 連結，從 %(oldcat)s 至 %(newcat)s',
}


class CommonscatBot:

    def __init__(self, generator, always, summary=None):
        self.generator = generator
        self.always = always
        self.summary = summary
        self.site = pywikibot.getSite()

    def run(self):
        for page in self.generator:
            self.treat(page)

    def treat(self, page):
        """ Loads the given page, does some changes, and saves it. """
        if not page.exists():
            pywikibot.output(u'Page %s does not exist. Skipping.'
                             % page.title(asLink=True))
        elif page.isRedirectPage():
            pywikibot.output(u'Page %s is a redirect. Skipping.'
                             % page.title(asLink=True))
        elif page.isCategoryRedirect():
            pywikibot.output(u'Page %s is a category redirect. Skipping.'
                             % page.title(asLink=True))
        elif page.isDisambig():
            pywikibot.output(u'Page %s is a disambiguation. Skipping.'
                             % page.title(asLink=True))
        else:
            (status, always) = self.addCommonscat(page)
        return

    def load(self, page):
        """ Loads the given page, does some changes, and saves it. """
        try:
            text = page.get()
        except pywikibot.NoPage:
            pywikibot.output(u"Page %s does not exist; skipping."
                             % page.title(asLink=True))
        except pywikibot.IsRedirectPage:
            pywikibot.output(u"Page %s is a redirect; skipping."
                             % page.title(asLink=True))
        else:
            return text
        return None

    def save(self, text, page, comment, minorEdit=True, botflag=True):
        # only save if something was changed
        if text != page.get():
            # Show the title of the page we're working on.
            # Highlight the title in purple.
            pywikibot.output(u"\n\n>>> \03{lightpurple}%s\03{default} <<<"
                             % page.title())
            # show what was changed
            pywikibot.showDiff(page.get(), text)
            pywikibot.output(u'Comment: %s' % comment)
            if not self.always:
                choice = pywikibot.inputChoice(
                    u'Do you want to accept these changes?',
                    ['Yes', 'No', 'Always', 'Quit'],
                    ['y', 'N', 'a', 'q'], 'N')
                if choice == 'a':
                    self.always = True
                elif choice == 'q':
                    import sys
                    sys.exit()
            if self.always or choice == 'y':
                try:
                    # Save the page
                    page.put(text, comment=comment,
                             minorEdit=minorEdit, botflag=botflag)
                except pywikibot.LockedPage:
                    pywikibot.output(u"Page %s is locked; skipping."
                                     % page.title(asLink=True))
                except pywikibot.EditConflict:
                    pywikibot.output(
                        u'Skipping %s because of edit conflict'
                        % (page.title()))
                except pywikibot.SpamfilterError as error:
                    pywikibot.output(
                        u'Cannot change %s because of spam blacklist entry %s'
                        % (page.title(), error.url))
                else:
                    return True
        return False

    @classmethod
    def getCommonscatTemplate(self, lang=None):
        """Get the template name in a language. Expects the language code.
        Return as tuple containing the primary template and it's alternatives

        """
        if lang in commonscatTemplates:
            return commonscatTemplates[lang]
        else:
            return commonscatTemplates[u'_default']

    def skipPage(self, page):
        '''
        Do we want to skip this page?
        '''
        if page.site.language() in ignoreTemplates:
            templatesInThePage = page.templates()
            templatesWithParams = page.templatesWithParams()
            for template in ignoreTemplates[page.site.language()]:
                if type(template) != tuple:
                    for pageTemplate in templatesInThePage:
                        if pageTemplate.title(withNamespace=False) == template:
                            return True
                else:
                    for (inPageTemplate, param) in templatesWithParams:
                        if inPageTemplate.title(withNamespace=False) == template[0] \
                           and template[1] in param[0].replace(' ', ''):
                            return True
        return False

    def addCommonscat(self, page):
        """Take a page. Go to all the interwiki page looking for a commonscat
        template. When all the interwiki's links are checked and a proper
        category is found add it to the page.

        """
        pywikibot.output(u'Working on ' + page.title())
        # Get the right templates for this page
        primaryCommonscat, commonscatAlternatives = self.getCommonscatTemplate(
            page.site.language())
        commonscatLink = self.getCommonscatLink(page)
        if commonscatLink:
            pywikibot.output(u'Commonscat template is already on %s'
                             % page.title())
            (currentCommonscatTemplate,
             currentCommonscatTarget, LinkText, Note) = commonscatLink
            checkedCommonscatTarget = self.checkCommonscatLink(
                currentCommonscatTarget)
            if (currentCommonscatTarget == checkedCommonscatTarget):
                # The current commonscat link is good
                pywikibot.output(u'Commonscat link at %s to Category:%s is ok'
                                 % (page.title(), currentCommonscatTarget))
                return (True, self.always)
            elif checkedCommonscatTarget != u'':
                # We have a new Commonscat link, replace the old one
                self.changeCommonscat(page, currentCommonscatTemplate,
                                      currentCommonscatTarget,
                                      primaryCommonscat,
                                      checkedCommonscatTarget, LinkText, Note)
                return (True, self.always)
            else:
                #Commonscat link is wrong
                commonscatLink = self.findCommonscatLink(page)
                if (commonscatLink != u''):
                    self.changeCommonscat(page, currentCommonscatTemplate,
                                          currentCommonscatTarget,
                                          primaryCommonscat, commonscatLink)
                #else
                #Should i remove the commonscat link?

        elif self.skipPage(page):
            pywikibot.output("Found a template in the skip list. Skipping %s"
                             % page.title())
        else:
            commonscatLink = self.findCommonscatLink(page)
            if (commonscatLink != u''):
                if commonscatLink == page.title():
                    textToAdd = u'{{%s}}' % primaryCommonscat
                else:
                    textToAdd = u'{{%s|%s}}' % (primaryCommonscat,
                                                commonscatLink)
                (success, status, self.always) = add_text.add_text(page,
                                                                   textToAdd,
                                                                   self.summary,
                                                                   None, None,
                                                                   self.always)
                return (True, self.always)
        return (True, self.always)

    def changeCommonscat(self, page=None, oldtemplate=u'', oldcat=u'',
                         newtemplate=u'', newcat=u'', linktitle=u'',
                         description=u''):
        """ Change the current commonscat template and target. """
        if oldcat == '3=S' or linktitle == '3=S':
            return  # additional param on de-wiki, TODO: to be handled
        if not linktitle and (page.title().lower() in oldcat.lower() or
                              oldcat.lower() in page.title().lower()):
            linktitle = oldcat
        if linktitle and newcat != page.title(withNamespace=False):
            newtext = re.sub(u'(?i)\{\{%s\|?[^{}]*(?:\{\{.*\}\})?\}\}'
                             % oldtemplate,
                             u'{{%s|%s|%s}}' % (newtemplate, newcat, linktitle),
                             page.get())
        elif newcat == page.title(withNamespace=False):
            newtext = re.sub(u'(?i)\{\{%s\|?[^{}]*(?:\{\{.*\}\})?\}\}'
                             % oldtemplate,
                             u'{{%s}}' % newtemplate,
                             page.get())
        elif oldcat.strip() != newcat:  # strip trailing white space
            newtext = re.sub(u'(?i)\{\{%s\|?[^{}]*(?:\{\{.*\}\})?\}\}'
                             % oldtemplate,
                             u'{{%s|%s}}' % (newtemplate, newcat),
                             page.get())
        else:  # nothing left to do
            return
        if self.summary:
            comment = self.summary
        else:
            comment = pywikibot.translate(page.site(),
                                          msg_change) % {'oldcat': oldcat,
                                                         'newcat': newcat}
        self.save(newtext, page, comment)

    def findCommonscatLink(self, page=None):
        # In Pywikibot 2.0, page.interwiki() now returns Link objects, not Page objects
        for ipageLink in page.langlinks():
            ipage = pywikibot.page.Page(ipageLink)
            pywikibot.log("Looking for template on %s" % (ipage.title()))
            try:
                if(ipage.exists() and not ipage.isRedirectPage()
                   and not ipage.isDisambig()):
                    commonscatLink = self.getCommonscatLink(ipage)
                    if commonscatLink:
                        (currentTemplate,
                         possibleCommonscat, linkText, Note) = commonscatLink
                        checkedCommonscat = self.checkCommonscatLink(
                            possibleCommonscat)
                        if (checkedCommonscat != u''):
                            pywikibot.output(
                                u"Found link for %s at [[%s:%s]] to %s."
                                % (page.title(), ipage.site.language(),
                                   ipage.title(), checkedCommonscat))
                            return checkedCommonscat
            except pywikibot.BadTitle:
                #The interwiki was incorrect
                return u''
        return u''

    def getCommonscatLink(self, wikipediaPage=None):
        '''
        Go through the page and return a tuple of (<templatename>, <target>)
        '''
        primaryCommonscat, commonscatAlternatives = self.getCommonscatTemplate(
            wikipediaPage.site.language())
        commonscatTemplate = u''
        commonscatTarget = u''
        commonscatLinktext = u''
        commonscatNote = u''
        # See if commonscat is present
        for template in wikipediaPage.templatesWithParams():
            templateTitle = template[0].title(withNamespace=False)
            if templateTitle == primaryCommonscat \
               or templateTitle in commonscatAlternatives:
                commonscatTemplate = templateTitle
                if (len(template[1]) > 0):
                    commonscatTarget = template[1][0]
                    if len(template[1]) > 1:
                        commonscatLinktext = template[1][1]
                    if len(template[1]) > 2:
                        commonscatNote = template[1][2]
                else:
                    commonscatTarget = wikipediaPage.title(withNamespace=False)
                return (commonscatTemplate, commonscatTarget,
                        commonscatLinktext, commonscatNote)
        return None

    def checkCommonscatLink(self, name=""):
        """ This function will return the name of a valid commons category
        If the page is a redirect this function tries to follow it.
        If the page doesnt exists the function will return an empty string

        """
        pywikibot.log("getCommonscat: " + name)
        try:
            commonsSite = self.site.image_repository()
            #This can throw a pywikibot.BadTitle
            commonsPage = pywikibot.Page(commonsSite, "Category:" + name)

            if not commonsPage.exists():
                pywikibot.output(u'Commons category does not exist. Examining deletion log...')
                logpages = commonsSite.logevents(logtype='delete', page=commonsPage)
                for logitem in logpages:
                    logitem = next(logpages)
                    (logpage, loguser, logtimestamp, logcomment) = logitem
                    # Some logic to extract the target page.
                    regex = u'moved to \[\[\:?Category:(?P<newcat1>[^\|\}]+)(\|[^\}]+)?\]\]|Robot: Changing Category:(.+) to Category:(?P<newcat2>.+)'
                    m = re.search(regex, logcomment, flags=re.I)
                    if m:
                        if m.group('newcat1'):
                            return self.checkCommonscatLink(m.group('newcat1'))
                        elif m.group('newcat2'):
                            return self.checkCommonscatLink(m.group('newcat2'))
                    else:
                        pywikibot.output(
                            u'getCommonscat: Deleted by %s. Couldn\'t find '
                            u'move target in "%s"'
                            % (loguser, logcomment))
                        return u''
                return u''
            elif commonsPage.isRedirectPage():
                pywikibot.log(u"getCommonscat: The category is a redirect")
                return self.checkCommonscatLink(
                    commonsPage.getRedirectTarget().title(withNamespace=False))
            elif "Category redirect" in commonsPage.templates():
                pywikibot.log(u"getCommonscat: The category is a category redirect")
                for template in commonsPage.templatesWithParams():
                    if (template[0] == "Category redirect" and
                            len(template[1]) > 0):
                        return self.checkCommonscatLink(template[1][0])
            elif commonsPage.isDisambig():
                pywikibot.log(u"getCommonscat: The category is disambiguation")
                return u''
            else:
                return commonsPage.title(withNamespace=False)
        except pywikibot.BadTitle:
            # Funky title so not correct
            return u''
        except pywikibot.PageNotFound:
            return u''


def main():
    """ Parse the command line arguments and get a pagegenerator to work on.
    Iterate through all the pages.
    """

    summary = None
    generator = None
    checkcurrent = False
    always = False
    ns = []
    ns.append(14)
    # Load a lot of default generators
    genFactory = pagegenerators.GeneratorFactory()

    for arg in pywikibot.handleArgs():
        if arg.startswith('-summary'):
            if len(arg) == 8:
                summary = pywikibot.input(u'What summary do you want to use?')
            else:
                summary = arg[9:]
        elif arg.startswith('-checkcurrent'):
            checkcurrent = True
            primaryCommonscat, commonscatAlternatives = \
                CommonscatBot.getCommonscatTemplate(
                    pywikibot.getSite().language())
            generator = pagegenerators.NamespaceFilterPageGenerator(
                pagegenerators.ReferringPageGenerator(
                    pywikibot.Page(pywikibot.getSite(),
                                   u'Template:' + primaryCommonscat),
                    onlyTemplateInclusion=True), ns)

        elif arg == '-always':
            always = True
        else:
            genFactory.handleArg(arg)

    if not generator:
        generator = genFactory.getCombinedGenerator()
    if not generator:
        raise add_text.NoEnoughData(u'You have to specify the generator you '
                                    u'want to use for the script!')

    pregenerator = pagegenerators.PreloadingGenerator(generator)
    bot = CommonscatBot(pregenerator, always, summary)
    bot.run()

if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()
