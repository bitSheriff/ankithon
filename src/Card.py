
class Card:
  txt = ''
  title = ''
  level = -1
  domain = ['', '', '', '', '', '']
  lvl_id = 0

  def get_title_plain(self):
    return self.title[4:].strip()

  def get_title_md(self):
    return self.title

  def get_domain_plain(self, d):
    return self.domain[d].strip()

  def get_deck_name(self):
    if len(self.domain[0]) == 0:
      print("Domain 0 is empty")
      return 'Unknown'

    deck_str = self.domain[0]
    for i in range(1,5):
        deck = self.get_domain_plain(i)
        if len(deck) == 0:
            return deck_str
        deck_str = deck_str + "::" + deck
    print(deck_str)
    return deck_str

  def set_nth_domain(self, n, name):
      # print("Nth: " + str(n) + " Name: " + name)
      name = name.replace("#", "").strip()
      if n < 0 or n > 5:
          raise ValueError("Invalid domain index")
      self.domain[n] = name
