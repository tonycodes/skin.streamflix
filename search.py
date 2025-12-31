import xbmc
import xbmcgui
import xbmcaddon
import json
import threading
import time

ADDON = xbmcaddon.Addon()
ADDON_PATH = ADDON.getAddonInfo('path')

class SearchWindow(xbmcgui.WindowXML):
    def __init__(self, *args, **kwargs):
        self.search_term = ''
        self.results = []
        self.search_thread = None
        self.last_search = ''

    def onInit(self):
        self.list_control = self.getControl(50)
        self.search_label = self.getControl(100)
        self.results_label = self.getControl(101)
        self.update_display()

    def update_display(self):
        # Update search term display
        if self.search_term:
            self.search_label.setLabel(self.search_term)
        else:
            self.search_label.setLabel('Type to search...')

        # Update results count
        if self.results:
            self.results_label.setLabel(f'{len(self.results)} results')
        else:
            self.results_label.setLabel('')

    def do_search(self):
        """Perform the actual search."""
        if not self.search_term or self.search_term == self.last_search:
            return

        self.last_search = self.search_term
        results = []

        # Search movies
        movie_query = {
            "jsonrpc": "2.0",
            "method": "VideoLibrary.GetMovies",
            "params": {
                "filter": {
                    "field": "title",
                    "operator": "contains",
                    "value": self.search_term
                },
                "properties": ["title", "year", "art", "file", "genre", "rating"],
                "sort": {"order": "ascending", "method": "title"},
                "limits": {"start": 0, "end": 50}
            },
            "id": 1
        }

        movie_response = xbmc.executeJSONRPC(json.dumps(movie_query))
        movie_data = json.loads(movie_response)

        if 'result' in movie_data and 'movies' in movie_data['result']:
            for movie in movie_data['result']['movies']:
                results.append({
                    'type': 'movie',
                    'label': movie['title'],
                    'label2': f"Movie • {movie.get('year', '')}",
                    'year': movie.get('year', ''),
                    'file': movie.get('file', ''),
                    'poster': movie.get('art', {}).get('poster', ''),
                    'fanart': movie.get('art', {}).get('fanart', ''),
                    'movieid': movie.get('movieid', 0)
                })

        # Search TV shows
        tv_query = {
            "jsonrpc": "2.0",
            "method": "VideoLibrary.GetTVShows",
            "params": {
                "filter": {
                    "field": "title",
                    "operator": "contains",
                    "value": self.search_term
                },
                "properties": ["title", "year", "art", "file", "genre", "rating"],
                "sort": {"order": "ascending", "method": "title"},
                "limits": {"start": 0, "end": 50}
            },
            "id": 2
        }

        tv_response = xbmc.executeJSONRPC(json.dumps(tv_query))
        tv_data = json.loads(tv_response)

        if 'result' in tv_data and 'tvshows' in tv_data['result']:
            for show in tv_data['result']['tvshows']:
                results.append({
                    'type': 'tvshow',
                    'label': show['title'],
                    'label2': f"TV Show • {show.get('year', '')}",
                    'year': show.get('year', ''),
                    'file': show.get('file', ''),
                    'poster': show.get('art', {}).get('poster', ''),
                    'fanart': show.get('art', {}).get('fanart', ''),
                    'tvshowid': show.get('tvshowid', 0)
                })

        self.results = results
        self.update_results_list()

    def update_results_list(self):
        """Update the results list control."""
        self.list_control.reset()

        for item in self.results:
            li = xbmcgui.ListItem(item['label'], item['label2'])
            li.setArt({
                'poster': item.get('poster', ''),
                'thumb': item.get('poster', ''),
                'fanart': item.get('fanart', '')
            })
            li.setProperty('type', item['type'])
            if item['type'] == 'movie':
                li.setProperty('movieid', str(item.get('movieid', 0)))
                li.setProperty('file', item.get('file', ''))
            else:
                li.setProperty('tvshowid', str(item.get('tvshowid', 0)))
            self.list_control.addItem(li)

        self.update_display()

    def onAction(self, action):
        action_id = action.getId()

        # Back/Escape
        if action_id in [92, 10, 110]:
            self.close()
            return

        # Backspace
        if action_id == 61448 or action_id == 110:
            if self.search_term:
                self.search_term = self.search_term[:-1]
                self.update_display()
                self.do_search()
            return

        # Get button code for letter input
        button_code = action.getButtonCode()

        # Handle letter/number input (ASCII printable characters)
        if action_id >= 61505 and action_id <= 61530:  # a-z
            char = chr(action_id - 61505 + ord('a'))
            self.search_term += char
            self.update_display()
            self.do_search()
        elif action_id >= 61488 and action_id <= 61497:  # 0-9
            char = chr(action_id - 61488 + ord('0'))
            self.search_term += char
            self.update_display()
            self.do_search()
        elif action_id == 61536:  # Space
            self.search_term += ' '
            self.update_display()
            self.do_search()

    def onClick(self, controlId):
        if controlId == 50:  # Results list
            item = self.list_control.getSelectedItem()
            if item:
                item_type = item.getProperty('type')
                if item_type == 'movie':
                    file_path = item.getProperty('file')
                    if file_path:
                        self.close()
                        xbmc.executebuiltin(f'PlayMedia("{file_path}")')
                elif item_type == 'tvshow':
                    tvshowid = item.getProperty('tvshowid')
                    if tvshowid:
                        self.close()
                        xbmc.executebuiltin(f'ActivateWindow(Videos,videodb://tvshows/titles/{tvshowid}/,return)')

        elif controlId == 9001:  # Back button
            self.close()

        # Keyboard buttons (A-Z)
        elif controlId >= 1001 and controlId <= 1026:
            char = chr(controlId - 1001 + ord('A'))
            self.search_term += char.lower()
            self.update_display()
            self.do_search()

        # Number buttons (0-9)
        elif controlId >= 1100 and controlId <= 1109:
            char = str(controlId - 1100)
            self.search_term += char
            self.update_display()
            self.do_search()

        # Space button
        elif controlId == 1200:
            self.search_term += ' '
            self.update_display()
            self.do_search()

        # Backspace button
        elif controlId == 1201:
            if self.search_term:
                self.search_term = self.search_term[:-1]
                self.update_display()
                self.do_search()

        # Clear button
        elif controlId == 1202:
            self.search_term = ''
            self.results = []
            self.list_control.reset()
            self.update_display()


def main():
    window = SearchWindow('SearchWindow.xml', ADDON_PATH, 'Default', '1080p')
    window.doModal()
    del window

if __name__ == '__main__':
    main()
