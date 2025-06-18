
class Card:
  txt = ''
  title = ''
  level = -1
  domain = ['', '', '']
  lvl_id = 0

  def get_title_plain(self):
    return self.title[4:].strip()

  def get_title_md(self):
    return self.title

  def get_domain_plain(self, d):
    return self.domain[d][(d+2):].strip()

  def get_deck_name(self):
    if len(self.domain[0]) == 0:
      return 'Unknown'
    elif len(self.domain[1]) > 0:
      return self.get_domain_plain(0) + '::' + self.get_domain_plain(1)
    else:
      return self.get_domain_plain(0)
