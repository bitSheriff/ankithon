import genanki
import random
import os
from shutil import copyfile, rmtree
import re
from markdown2 import Markdown

from Card import Card

class Transformer:
  all_decks = []
  deck = None
  model = None
  package = None

  img_links = []
  img_counter = 0
  markdowner = Markdown(extras=["tables"])
  mediadir = './md2a_media/'
  fbase = None
  fbase_dir = None

  def process(self, src_file, dst_file, fbase, fbase_dir, style):

    self.fbase = fbase
    self.fbase_dir = fbase_dir

    self.model = self.make_model(style)

    self.md_fill_deck(src_file)
    self.package = genanki.Package(self.all_decks)
    self.package.media_files = self.img_links
    self.package.write_to_file(dst_file)
    rmtree(self.mediadir)

  def md_fill_deck(self, src_file):

    if not os.path.exists(self.mediadir):
      os.makedirs(self.mediadir)

    ccounter = 0
    card = Card()
    card.set_nth_domain(0, self.fbase)
    max_level = get_max_level(src_file)
    if max_level <= 1:
        print("Max Level not enough; I needs one heading for the deck")
        exit(2);

    with open(src_file, 'r', encoding='utf-8') as myfile:
      for line in myfile:
        h = h_level(line)
        if h > 0:  # new card start
          if card.level == max_level and ccounter > 0:  # make old card
            self.md_make_card(card)

          # setup new card
          card.level = h
          if not h == max_level:
            card.set_nth_domain(card.level-1, line)
          card.title = line
          card.txt = ''

          if not card.level == max_level:
            card.lvl_id = 0
            if not self.deck == None:
              self.all_decks.append(self.deck)
            self.deck = genanki.Deck(
              random.randrange(1 << 30, 1 << 31),
              card.get_deck_name())
            print(card.get_deck_name())

          if card.level == 3:
            card.lvl_id += 1
            ccounter += 1

        else:  # just text -> add to card
          card.txt += line

      if card.level == max_level and ccounter > 0:  # make last card
        self.md_make_card(card)

    self.all_decks.append(self.deck)
    print('Added', ccounter, 'cards with',self.img_counter,'images in',len(self.all_decks),'decks.')


  def md_make_card(self, card):

    if self.deck == None:
      self.deck = genanki.Deck(
        random.randrange(1 << 30, 1 << 31),
        card.get_deck_name())

    buff = 0
    buff_ctxt = ''
    for img in re.finditer(r'(?:!\[(.*?)\]\((\S*)( =(\d*)x(\d*))?\))', card.txt):
      m_alt = img.group(1)
      m_path = self.fbase_dir+img.group(2)
      npath = str(self.img_counter) + os.path.splitext(m_path)[1]
      self.img_counter += 1

      if os.path.exists(m_path):
        copyfile(m_path, self.mediadir + npath)
        self.img_links.append(self.mediadir + npath)
      else:
        print("WARNING: Image not found ('"+m_path+"')")

      m_width = img.group(4)
      m_height = img.group(5)
      blob = '<img src="' + npath + '"'
      if (not m_alt == None):
        blob += ' alt="'+m_alt+'"'
      if (not m_width == None and len(m_width.strip()) > 0):
        blob += ' width="'+m_width.strip()+'"'
      if (not m_height == None and len(m_height.strip()) > 0):
        blob += ' height="'+m_height.strip()+'"'
      blob += '>'

      buff_ctxt += card.txt[buff:img.start()] + blob
      buff = img.end()


    buff_ctxt += card.txt[buff:len(card.txt)]
    card.txt = buff_ctxt

    self.deck.add_note(genanki.Note(
      model=self.model,
      fields=[
        self.markdowner.convert(card.get_title_md()).strip(),
        self.markdowner.convert(card.txt).strip()]))

    # tags=[re.sub(r'#*','',cdomain[0]).strip().replace(' ','_'),re.sub(r'#*','',cdomain[1]).strip().replace(' ','_')])

  def make_model(self, style):
        m_id = 1395453623
        m_name = 'ankithon simple v1'
        if len(style) > 0:
            m_id = random.randrange(1 << 30, 1 << 31)
            m_name += ' (styled)'
        return genanki.Model(
            m_id,
            m_name,
            fields=[
            {'name': 'Question'},
            {'name': 'Answer'},
            ],
            templates=[
            {
                'name': 'Card 1',
                'qfmt': '<article class="markdown-body">{{Question}}</article>',
                'afmt': '<article class="markdown-body">{{FrontSide}}</article><hr id="answer"><article class="markdown-body">{{Answer}}</article>',
            },
            ], css=style)


def h_level(txt):
    # the maximum heading level in (standard) markdown is 6
    for i in range(6, 0, -1):
        if txt.startswith(i*'#'):
            return i
    return 0

def get_max_level(src_file) -> int:
       max_h_level = 0
       with open(src_file, 'r', encoding='utf-8') as myfile:
           for line in myfile:
               h = h_level(line)
               if h > max_h_level:
                   max_h_level = h
       return max_h_level

def strip_answers(src_file, dst_file, lvl):
   out_file = open(dst_file, 'w', encoding='utf-8')
   with open(src_file, 'r', encoding='utf-8') as myfile:
    for line in myfile:
      h = h_level(line)
      if h > 0 and h <= lvl:  # new card start
        out_file.write(line + '\n')
    out_file.close()
# re.sub(r'(?:!\[(.*?)\]\(((\S*/)\S*?)( =(\d*)x(\d)*)?\))', r'<img src="\4" width="\6" height="\7">', test)
