"""
Trello Export

Convert a Trello board JSON export to:
    1. A folder for the board with
    2. A subfolder for each list with
    3. A subfolder per card with
    4. An index.md file per card, containing its description and comments and links to
    5. Each attachment for the card. Images appear as embedded images in the markdown file.

Usage:
    Export your board to json (board > menu > more > print and export > export to JSON),
    saving it in the same folder as this script and then

    $ python trello_export.py <filename.json>

    Nothing to configure, no argument validation; quick and dirty.
"""

import json, os, os.path, unicodedata, urllib.request, sys, time

board_file = bytes(sys.argv[1], encoding='utf-8')

# These are the templates used for Markdown export. If you don't like the used
# format, edit here.

templates = {
  'comment': '''## %(date)s
%(text)s

''',
  ##########
  'note': '''# %(name)s
_%(date)s_
%(desc)s
''',
   #########
   'attachment': '''+ %(img_mark)s[%(name)s](%(path)s) (%(date)s)
''',
}

def get_url(url,filename):
    """Downloads and saves an attachment"""
    print("Getting %s -> %s" % (url, filename))
    try:
        with urllib.request.urlopen(url) as response, open(filename, 'wb') as out_file:
            data = response.read()
            out_file.write(data)
    except FileNotFoundError:
        print("%s not found" % filename)

def slugify(value, replace_spaces=False):
    """
    Normalizes string, converts to lowercase, removes non-alpha and "foreign"
    characters, removes forbidden characters, and converts spaces to underscores.
    Used for file and folder names.
    """
    replaced = ('/', '\\', ':', '$', '&', '!', '*', '~', '`', '"', '+', '>', '<', '?', '|', '¿', '~', '¡')
    for r in replaced:
      value = value.replace(r, '_')
    if replace_spaces:
      value = value.replace(' ', '_')
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    return value.strip()


if __name__ == '__main__':

    board = json.loads(open(board_file, encoding='utf-8').read())
    base_dir = os.path.splitext(board_file)[0]
    # Get all the lists and create their folders
    list_map = {}
    for list in board['lists']:
        list_map[list['id']]={
          'name': list['name'],
          'path': os.path.join(base_dir,slugify(list['name']))
         }
        os.makedirs(list_map[list['id']]['path'], exist_ok=True)
    # Get the comments and the creation dates of the cards
    # (these appear under the 'actions':{...}  element)
    comments = {}
    dates = {}
    for action in board['actions']:
      for k,v in action.items():
        if k=='type' and v=='commentCard':
          # print(action)
          cmt={
          'id' : action['data']['card']['id'],
          'card' : action['data']['card']['name'],
          'date' : action['date'].replace('T', ' ')[:-8],
          'text' : action['data']['text']
          }
          if cmt['id'] in comments.keys():
            comments[cmt['id']].append(cmt)
          else:
            comments[cmt['id']] = [cmt,]
        if k=='type' and v=='createCard':
          dates[action['data']['card']['id']] = action['date'].replace('T', ' ')[:-8]

    # Get the cards (under 'cards': {...})
    cards = {}
    for card in board['cards']:
      # sometimes we won't find the creation date in the actions,
      # so we assign one.
      if card['id'] in dates:
          cdate = dates[card['id']]
      else:
          cdate = time.strftime("%y-%m-%d")
      cards[card['id']] = {
        'id': card['id'],
        'name': card['name'],
        'fname': slugify(card['name']),
        'list': list_map[card['idList']]['name'],
        'path': os.path.join(list_map[card['idList']]['path'], slugify(card['name'])),
        'desc': card['desc'],
        'date': cdate,
        'attachments': card['attachments']
      }

    # Create the actual cards and its foders
    for card_id, card in cards.items():
        card_content = templates['note'] % card
        if card_id in comments.keys():
            for cmt in comments[card_id]:
                card_content+= templates['comment'] % cmt
        os.makedirs(card['path'], exist_ok=True)
        # Download attachments
        atch_path = card['path'] # originally we added a folder for attachments. Left here should someone need it.
        for atch in card['attachments']:
            # os.makedirs(atch_path, exist_ok=True)
            get_url(atch['url'], os.path.join(atch_path,slugify(atch['name'], replace_spaces=True)))
            atch['name'] = atch['name'].replace('_', ' ')
            # Images will be inserted as Markdown images, not mere links.
            if os.path.splitext(atch['name'])[1] in ('.jpg', '.gif', '.png', '.jpeg'):
                atch['img_mark'] = '!'
            else:
                atch['img_mark'] = ''
            atch['path'] = slugify(atch['name'], replace_spaces=True).decode('utf-8') #.replace('_', ' ')
            atch['date'] = atch['date'].replace('T', ' ')[:-8]
            card_content+= templates['attachment'] % atch
        open(os.path.join(card['path'], b'index.md'), 'w', encoding='utf-8').write(card_content)
