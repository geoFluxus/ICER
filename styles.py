import matplotlib.pyplot as plt

COLORS = {"A": '#39B54A',
          "B": '#8CC63F',
          "C": '#D9E021',
          "D": '#FCEE21',
          "E": '#FBB03B',
          "F": '#F7931E',
          "G": '#F15A24',
          "H": "#CC3333",
          "I": '#4D4D4D'
          }

colors_list = [
     "#F98517","#E83326","#921893","#1077F3","#4AB58A","#FBE308","#FFB46D","#FF8F7C","#9B54F3","#0050AE","#C2D967",
     "#E1957B","#BE4CBF","#BF8CFC","#7018D3","#728E03","#D0BB00","#C85B00","#680000","#999CE1","#008C5C","#91BFC9",
     "#9EB933","#D56F7B","#C3C49A","#AC0000","#92C797","#69016A","#002F64","#00603D"]

colors_list_3 = ["#f98517", "#72b622", "#bf8cfc", "#5ba8f7", "#e83326", "#c6a000", "#33b983", "#ee74ee", "#1077f3", "#008c5c"]
colors_list_2 = ['#aa75ff', '#7f43df', '#5f319f', '#002993', '#0048ff', '#1597ee', '#012646', '#003666', '#009e9b',
                 '#893700', '#004242', '#ee5396', '#e50063', '#b7004f', '#ff5d00', '#b28500', '#520307', '#0d441a',
                 '#197f37', '#00ad28']

col = [(235, 172, 35), (184, 0, 88), (0, 140, 249), (0, 110, 0), (0, 187, 173), (209, 99, 230), (178, 69, 2), (255, 146, 135), (89, 84, 214), (0, 198, 248), (135, 133, 0), (0, 167, 108), (189, 189, 189)]
cols = []
for i in range(len(col)):
    c = (col[i][0]/255,col[i][1]/255,col[i][2]/255)
    cols.append(c)

params = {'legend.fontsize': 'xx-small',
          'axes.labelsize': 'xx-small',
          'axes.titlesize': 'x-small',
          'axes.grid': True,
          'axes.grid.axis': 'y',
          'axes.grid.which': 'major',
          'axes.axisbelow': True,
          'grid.color': 'white',
          'xtick.labelsize': 'x-small',
          'ytick.labelsize': 'x-small',
          'axes.edgecolor': 'white',
          'axes.facecolor': '#EBEBEB',
          'axes.labelcolor': 'black',
          'figure.facecolor': 'white',
          'text.color': 'black',
          'xtick.color': 'black',
          'ytick.color': 'black',
          'legend.edgecolor': 'white',
          'axes.spines.top': False,
          'axes.spines.right': False,
          'axes.spines.left': True,
          'axes.formatter.useoffset': False,
          'lines.marker': 'o',
          'font.family': 'sans-serif',
          'figure.figsize': (8, 8),
          }


all_colors = ['aliceblue', 'antiquewhite', 'aqua', 'aquamarine', 'azure',
            'beige', 'bisque', 'black', 'blanchedalmond', 'blue',
            'blueviolet', 'brown', 'burlywood', 'cadetblue',
            'chartreuse', 'chocolate', 'coral', 'cornflowerblue',
            'cornsilk', 'crimson', 'cyan', 'darkblue', 'darkcyan',
            'darkgoldenrod', 'darkgray', 'darkgrey', 'darkgreen',
            'darkkhaki', 'darkmagenta', 'darkolivegreen', 'darkorange',
            'darkorchid', 'darkred', 'darksalmon', 'darkseagreen',
            'darkslateblue', 'darkslategray', 'darkslategrey',
            'darkturquoise', 'darkviolet', 'deeppink', 'deepskyblue',
            'dimgray', 'dimgrey', 'dodgerblue', 'firebrick',
            'floralwhite', 'forestgreen', 'fuchsia', 'gainsboro',
            'ghostwhite', 'gold', 'goldenrod', 'gray', 'grey', 'green',
            'greenyellow', 'honeydew', 'hotpink', 'indianred', 'indigo',
            'ivory', 'khaki', 'lavender', 'lavenderblush', 'lawngreen',
            'lemonchiffon', 'lightblue', 'lightcoral', 'lightcyan',
            'lightgoldenrodyellow', 'lightgray', 'lightgrey',
            'lightgreen', 'lightpink', 'lightsalmon', 'lightseagreen',
            'lightskyblue', 'lightslategray', 'lightslategrey',
            'lightsteelblue', 'lightyellow', 'lime', 'limegreen',
            'linen', 'magenta', 'maroon', 'mediumaquamarine',
            'mediumblue', 'mediumorchid', 'mediumpurple',
            'mediumseagreen', 'mediumslateblue', 'mediumspringgreen',
            'mediumturquoise', 'mediumvioletred', 'midnightblue',
            'mintcream', 'mistyrose', 'moccasin', 'navajowhite', 'navy',
            'oldlace', 'olive', 'olivedrab', 'orange', 'orangered',
            'orchid', 'palegoldenrod', 'palegreen', 'paleturquoise',
            'palevioletred', 'papayawhip', 'peachpuff', 'peru', 'pink',
            'plum', 'powderblue', 'purple', 'red', 'rosybrown',
            'royalblue', 'rebeccapurple', 'saddlebrown', 'salmon',
            'sandybrown', 'seagreen', 'seashell', 'sienna', 'silver',
            'skyblue', 'slateblue', 'slategray', 'slategrey', 'snow',
            'springgreen', 'steelblue', 'tan', 'teal', 'thistle', 'tomato',
            'turquoise', 'violet', 'wheat', 'white', 'whitesmoke',
            'yellow', 'yellowgreen']