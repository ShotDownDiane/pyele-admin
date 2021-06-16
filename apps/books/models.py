import os
import re
from requests_html import HTMLSession
from django.db import models
from EraAdmin import utools
from EraAdmin.models import BaseModel

class NovelChapter(BaseModel):
    chapter_id = models.AutoField(primary_key=True, help_text="章节ID")
    am_id = models.IntegerField(help_text="amID")
    am_chapter_id = models.IntegerField(help_text="amChapterID")
    am_path = models.CharField(default="", max_length=128)
    name = models.CharField(default="", max_length=255, help_text="章节名称")
    number = models.CharField(default="", max_length=50, help_text="章节编号")
    content = models.TextField(default=None)
    xh = models.IntegerField(default=None, help_text="章节序号")
    title = models.CharField(default="", max_length=255, help_text="章节标题")

    class Meta:
        app_label = 'books'
        db_table = 'novel_chapter'

    def grabContent(self, site_id=100):
        if site_id == 100:
            session = HTMLSession()
            url = "https://m.amxs.cc/book/" + str(self.am_id) + "/" + str(self.am_chapter_id) + ".html"
            req = session.get(url)
            if req.status_code != 200:
                return False
            novelContent = req.html.find("#novelcontent p", first=True).html
            # SEO词汇去除
            novelContent = novelContent.replace("艾米小说网欢迎您!<br />", "").replace(
                "本站网址通俗好记,艾米小说网的汉字拼音首字母<br />", "").replace(
                r'(m.amxs.cc = <a href="https://m.amxs.cc">艾米小说网</a>)<br />', "")
            self.content = novelContent
            return novelContent
        else:
            return None

class Novel(BaseModel):
    novel_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128)
    author_id = models.CharField(max_length=20, default="")
    author_name = models.CharField(max_length=64)
    am_id = models.CharField(max_length=20)
    classify = models.CharField(max_length=20)
    site_name = models.CharField(max_length=20)
    site_id = models.CharField(max_length=10)
    site_page = models.CharField(max_length=255)
    state = models.CharField(max_length=10)
    intro = models.TextField()
    last_update_time = models.DateTimeField()
    cover_image = models.CharField(max_length=255)
    chapter = models.CharField(max_length=40)
    chapter_s = models.CharField(max_length=20)
    status = models.CharField(max_length=20)
    classify_name = models.CharField(max_length=20)
    title = models.CharField(max_length=128)
    check_status = models.CharField(max_length=10)
    custom = models.CharField(max_length=100)

    class Meta:
        app_label = 'books'
        db_table = 'novel'

    def downloadBookCover(self, url):
        # 这里做个小技巧，如果已经存在，则直接移动
        # 判断文件是否存在
        srcfile = utools.convert_path("C:\\Users\\NayMiku\\PycharmProjects\\test\data\\article\\" + str(
            self.am_id) + "\\images\\cover_s.jpg")
        dstfile = utools.convert_path("E:\\Books\\cover\\s\\" + str(self.novel_id) + ".jpg")
        if os.path.exists(srcfile):
            return utools.moveFile(srcfile, dstfile)
        else:
            return utools.download(url, dstfile)

    def getBookInfo(self, isUpdate=False):
        book_id = str(self.am_id)
        if self.site_id == 100:
            session = HTMLSession()
            url = "https://m.amxs.cc/book/" + book_id + "/"
            req = session.get(url)
            cover_img = list(req.html.find(".infohead .pic", first=True).xpath("//img/@src"))[0]
            # 下载封面图片到硬盘中
            self.downloadBookCover("https://m.amxs.cc" + cover_img)

            p = list(req.html.find(".infohead .infotype p"))
            name = req.html.find(".infohead .cataloginfo h3", first=True).text
            f_type = p[1].text
            status = p[2].text
            last_update_time = p[3].text
            state = 1
            intro = req.html.find(".infohead .intro p", first=True).text
            # 删除简介中的SEO内容
            intro = \
                intro.split(name + "最新章节," + name + "无弹窗,")[0].split(
                    "各位书友要是觉得《" + name + "》还不错的话请不要忘记向您QQ群和微博里的朋友推荐哦！")[0]
            # 注释部分是使用js技术获取内容的代码
            # script = """
            #         () => {
            #             return {
            #                chapter: $("select[name=pageselect] option")[$("select[name=pageselect] option").length -1].text
            #             }
            #         }
            # """
            # chapter = r.html.render(script=script, reload=True)
            a = list(req.html.find("select[name=pageselect]:last", first=True).text.split("\n"))
            chapter = {
                'chapter': a[len(a) - 1]
            }
            # 错误文章可能会导致时间错误，这里处理一下
            if len(last_update_time) != 22:
                last_update_time = "2020-01-01 12:00:00"
            data = {
                "name": name,
                "type": f_type[3:],
                "status": status[3:],
                "last_update_time": utools.utc_to_local(last_update_time[3:], "%Y-%m-%dT%H:%M:%S").strftime(
                    "%Y-%m-%d %H:%M:%S"),
                'state': state,
                'intro': intro,
                'chapter': chapter['chapter'],
                "cover_image": cover_img,
                "check_status": "ok"
            }
            if isUpdate:
                for field, value in data.items():
                    self.__setattr__(field, value)
                self.save()
            return data
        else:
            return None

    def getChapterInfo(self, isUpdate=False):
        book_id = str(self.am_id)
        if self.site_id == 100:
            if self.chapter is None:
                return False
            p = list(re.findall(r'^(.*) - (.*)章', self.chapter)[0])
            if len(p) != 2:
                return False
            maxStart = int(p[0])
            maxEnd = int(p[1])
            startPage = int(maxEnd / 20)
            url = "https://m.amxs.cc/book/" + book_id + "_" + str(startPage) + "/#all"
            session = HTMLSession()
            req = session.get(url)
            chapterList = req.html.find(".info_menu1 .list_xm")[1].find("ul li")
            chapter = maxStart + len(chapterList) - 1
            if isUpdate:
                self.chapter_s = chapter
                self.save()
            return chapter
        else:
            return None

    def getChapterList(self, chapter=None, debugPrint=False, callback=None):
        book_id = str(self.am_id)
        if self.chapter_s is None:
            self.chapter_s = self.getChapterInfo(isUpdate=True)
        if self.chapter_s is None or self.chapter_s is False:
            return False
        if self.site_id == 100:
            # 最大章节
            maxChapter = int(self.chapter_s)
            # 起始查询章节
            startChapter = 0
            # 结束章节
            endChapter = maxChapter
            # 每页限制是20
            page = 0
            limit = 20
            # 得到最大页数
            if maxChapter % limit == 0:
                maxPage = int(maxChapter / limit)
            else:
                maxPage = int(maxChapter / limit) + 1
            # 如果设置查询指定章节位置
            if chapter:
                if type(chapter) == list:
                    startChapter = chapter[0]
                    if len(chapter) == 2:
                        endChapter = chapter[1]
                    if startChapter > endChapter:
                        a = startChapter
                        startChapter = endChapter
                        endChapter = a
                    if endChapter > maxChapter:
                        endChapter = maxChapter
                else:
                    startChapter = chapter
            if startChapter > maxChapter:
                return False
            # 从起数开始算还是起数后面开始算的区别
            # startChapter = startChapter - 1
            if startChapter < 0:
                startChapter = 0
            if startChapter < limit:
                page = 1
            else:
                if startChapter % limit == 0:
                    page = int(startChapter / limit)
                else:
                    page = int(startChapter / limit) + 1
            if endChapter % limit == 0:
                endPage = int(endChapter / limit)
            else:
                endPage = int(endChapter / limit) + 1

            if endPage < page:
                endPage = page

            if debugPrint:
                print("amId:" + book_id + ",小说名：" + self.name + " [总章数:" + str(maxChapter) + "]从第" + str(
                    startChapter) + "章查询到" + str(endChapter) + "章",
                      "[总页数: " + str(maxPage) + "]从第" + str(page) + "页查询到" + str(endPage) + "页")
            session = HTMLSession()
            while page <= endPage:
                url = "https://m.amxs.cc/book/" + book_id + "_" + str(page) + "/#all"
                req = session.get(url)
                # 获取章节列表数据
                chapterList = req.html.find(".info_menu1 .list_xm")[1].find("ul li")
                # 获取当前页第一个数据起点
                _xh = (page - 1) * limit + 1
                # print("当前xh开始", _xh)
                # 遍历章节列表中的数据
                for item in chapterList:
                    if startChapter <= _xh <= endChapter:
                        text = list(item.links)[0]
                        ids = list(re.findall(r'^/book/(.*)/(.*).html', text)[0])
                        am_id = str(ids[0])
                        am_chapter_id = str(ids[1])
                        text2 = item.text
                        tna2 = re.findall(r'^第(.*)章(.*)', text2)
                        # 获取章节名称和序号，这里章节序号规律不正确。 如果上面第一种匹配规则不起作用，就不存序号，直接存储章节名称
                        if len(tna2) == 0:
                            tna = ["NULL", text2]
                        else:
                            tna = list(tna2[0])
                        name = tna[1]
                        number = tna[0]
                        # 查询数据
                        try:
                            NovelChapter.objects.values("chapter_id").get(am_id=am_id, am_chapter_id=am_chapter_id)
                        except NovelChapter.DoesNotExist:
                            novelChapter = NovelChapter(am_id=am_id, am_chapter_id=am_chapter_id, am_path="", name=name,
                                                        number=number,
                                                        content="", xh=_xh, title=text2)
                            novelChapter.save()
                            if callable(callback):
                                callback(novelChapter)
                        finally:
                            if debugPrint:
                                print("序号：" + str(
                                    _xh) + ", [小说Id: " + am_id + ", 章节ID:" + am_chapter_id + ", 章节名称:" + name + ", 章节号:" + number)
                    _xh = _xh + 1
                page = page + 1
        else:
            return None

    def getChapterContent(self, site_id, chapter_id=None, am_chapter_id=None, isUpdate=False):
        if self.site_id == 100:
            if chapter_id:
                novelChapter = NovelChapter.objects.get(chapter_id=chapter_id)
            elif am_chapter_id:
                novelChapter = NovelChapter.objects.get(am_chapter_id=am_chapter_id)
            else:
                return False
            novelContent = novelChapter.grabContent(site_id=site_id)
            if isUpdate:
                novelChapter.save()
            return novelContent
        else:
            return None
