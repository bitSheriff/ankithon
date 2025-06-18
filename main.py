# md2anki.py

import genanki
import random
from markdown2 import Markdown
import os
import argparse
import re
from shutil import copyfile, rmtree
import os, sys

sys.path.append("..")
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))
from src.Card import *
from src.Transformer import *

def main():
  parser = argparse.ArgumentParser(
      description='Convert markdown to anki deck.')

  parser.add_argument('INPUT', type=str, help='Input *.md path.')
  parser.add_argument('-o', '--output', type=str, help='Output *.apkg path.')
  parser.add_argument('-s', '--style', type=str, help='CSS card style path.')
  parser.add_argument('-q', '--questions', type=int, nargs='?', default=-1, const=3, help='Create *_questions.md with stripped answers. Optionally can be set to extract only set names. (2 = sub-decks; 1 = decks)')
  parser.add_argument('-w', '--web', action='store_true', help='Create *.html document.')

  args = parser.parse_args()

  src_file = args.INPUT

  if not os.path.exists(src_file):
    print('File not found:  \'', src_file+'\'')
    return

  fbase = os.path.splitext(os.path.basename(src_file))[0]
  fbase_dir = os.path.dirname(src_file)
  if len(fbase_dir) > 0:
    fbase_dir += '/'

  if args.questions >= 0:
    dst_file = fbase + '_questions.md'
    if args.output is not None:
      dst_file = args.output
    Transformer().strip_answers(src_file, dst_file, args.questions)
    return


  dst_file = fbase + '.apkg'

  style = ''
  style_path = fbase_dir+'style.css'

  if args.output is not None:
    dst_file = args.output
  if args.style is not None:
    style_path = args.style

  if args.web:
    dst_file = fbase + '.html'
    if args.output is not None:
      dst_file = args.output
    compile_html(src_file, dst_file, fbase, fbase_dir, style_path)
    return

  if os.path.exists(style_path):
    style = open(style_path, "r").read()

  print('Input:  \'', src_file+'\'')
  print('Output: \''+ dst_file+'\'')
  if (len(style) > 0):
    print('Using style: \''+style_path+'\'')
  Transformer().process(src_file, dst_file, fbase, fbase_dir, style)





def compile_html(src_file, dst_file, fbase, fbase_dir, style_path):
  mymd = ''
  with open(src_file, 'r', encoding='utf-8') as myfile:
    mymd = myfile.read()

  buff = 0
  buff_ctxt = ''
  for img in re.finditer(r'(?:!\[(.*?)\]\((\S*)( =(\d*)x(\d*))?\))', mymd):
    m_alt = img.group(1)
    m_path = fbase_dir+img.group(2)
    m_width = img.group(4)
    m_height = img.group(5)

    blob = '<img src="' + m_path + '"'
    if (not m_alt == None):
      blob += ' alt="'+m_alt+'"'
    if (not m_width == None and len(m_width.strip()) > 0):
      blob += ' width="'+m_width.strip()+'"'
    if (not m_height == None and len(m_height.strip()) > 0):
      blob += ' height="'+m_height.strip()+'"'
    blob += '>'

    buff_ctxt += mymd[buff:img.start()] + blob
    buff = img.end()

  buff_ctxt += mymd[buff:len(mymd)]
  mymd = buff_ctxt


  markdowner = Markdown(extras=["tables"])
  mymd = markdowner.convert(mymd)

  myhtml = '<!DOCTYPE html><html><head><meta charset="utf-8"/><link rel="stylesheet" href="'+style_path+'"><title>'+fbase+'</title></head><body><article class="markdown-body">'+mymd+'</article></body></html>'

  out_file = open(dst_file, 'w', encoding='utf-8')
  out_file.write(myhtml)
  out_file.close()

if __name__ == '__main__':
    main()

# print(data)
