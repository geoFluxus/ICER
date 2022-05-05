# a function that converts pandas dataframe into a sankey

import plotly.graph_objects as go
import pandas as pd
import matplotlib.pyplot as plt

def draw_sankey(df, scattered=False, title_text="Sankey Diagram"):

    # flatten sankey
    if scattered:
        df[df.columns[1]] = df[df.columns[1]] + df.index.astype(str)
    flat = []
    for i in range(len(df.columns) - 2):
        subdf = df[[df.columns[i], df.columns[i + 1], 'amount']]
        subdf = subdf.rename(columns={df.columns[i]: 'source',
                                      df.columns[i + 1]: 'target'})
        subdf['start_node'] = df[df.columns[0]]
        flat.append(subdf)
    flat = pd.concat(flat)

    nodes = list(flat['source']) + list(flat['target'])
    nodes = dict.fromkeys(nodes)
    c = 0
    for node in nodes.keys():
        nodes[node] = c
        c += 1

    cmap = plt.cm.get_cmap('Spectral')
    color_map = dict()
    start_nodes = list(flat['start_node'].drop_duplicates())
    step = 1.0 / len(start_nodes)
    node_colors = []
    for i in range(len(start_nodes)):
        rgba = cmap(i * step)
        rgba = tuple(int((255 * x)) for x in rgba[0:3]) + (0.5,)
        rgba = 'rgba' + str(rgba)
        color_map[start_nodes[i]] = rgba
        node_colors.append(rgba)

    # color_map = {'Afvalbeheer / secundair afval': 'rgba(255, 230, 0, 0.3)',
    #              'Buiten MRA': 'rgba(255, 145, 0, 0.3)',
    #              'Industrie, opslag en handel': 'rgba(229, 0, 130, 0.3)',
    #              'Overige': 'rgba(160, 0, 120, 0.3)',
    #              'Route Inzameling': 'rgba(0, 70, 153, 0.3)',
    #              'Dienstensector, overheid en zorg': 'rgba(41, 120, 142, 0.3)',
    #              'Bouwnijverheid': 'rgba(0, 157, 230, 0.3)',
    #              }

    start_nodes = list(flat['start_node'].drop_duplicates())
    node_colors = []
    for i in range(len(start_nodes)):
        rgba = color_map[start_nodes[i]]
        node_colors.append(rgba)

    # print(start_nodes)
    # print(color_map)

    sources = []
    targets = []
    values = []
    colors = []
    for index, row in flat.iterrows():
        sources.append(nodes[row['source']])
        targets.append(nodes[row['target']])
        values.append(row['amount'])
        colors.append(color_map[row['start_node']])

    fig = go.Figure(data=[go.Sankey(
                          # Define nodes
                          node=dict(pad=15,
                                    thickness=15,
                                    line=dict(color="black", width=0.01),
                                    label=list(nodes.keys()),
                                    color=node_colors
                                    ),
                          # Add links
                          link=dict(source=sources,
                                    target=targets,
                                    value=values,
                                    color=colors
                                    # label=[]
                                    ))])

    fig.update_layout(title_text=title_text,
                      font=dict(size = 10, color = 'black', family = 'Courier New'),
                      plot_bgcolor='#F2F2F3',
                      paper_bgcolor='#F2F2F3',
                      # plot_bgcolor='#070D22',
                      # paper_bgcolor='#070D22',
                      )
    fig.show()


def draw_circular_sankey(df, title_text="Sankey Diagram"):

        nodes = list(df['source']) + list(df['target'])
        nodes = dict.fromkeys(nodes)
        c = 0
        for node in nodes.keys():
            nodes[node] = c
            c += 1

        # POSITIONS
        source_nodes = list(set(df['source']))
        source_nodes.sort()
        target_nodes = [x for x in set(df['target']) if x not in source_nodes]
        target_nodes.sort()
        all_nodes = list(set([x[0] for x in source_nodes + target_nodes]))
        all_nodes.sort()
        # print(all_nodes)
        step = 0.8 / len(all_nodes)

        # list of consistent y positions since x position is fixed per column
        y_pos = dict()
        y = 0.1
        for nd in all_nodes:
            y_pos[nd] = y
            y += step

        snodes = dict()
        tnodes = dict()
        x = 0.1
        for nd in source_nodes:
            y = y_pos[nd[0]]
            snodes[nd] = (x, y)
            # print(nd, y)
        x = 0.9
        for nd in target_nodes:
            y = y_pos[nd[0]]
            tnodes[nd] = (x, y)
            # print(nd, y)

        snodes.update(tnodes)
        positions = snodes

        # RANDOM COLOURS
        # cmap = plt.cm.get_cmap('Spectral')
        # color_map = dict()
        # start_nodes = list(df['colour'].drop_duplicates())
        # step = 1.0 / len(start_nodes)
        # node_colors = []
        # for i in range(len(start_nodes)):
        #     rgba = cmap(i * step)
        #     rgba = tuple(int((255 * x)) for x in rgba[0:3]) + (0.5,)
        #     rgba = 'rgba' + str(rgba)
        #     color_map[start_nodes[i]] = rgba
        #     node_colors.append(rgba)
        #
        # start_nodes = list(df['colour'].drop_duplicates())
        # node_colors = []
        # for i in range(len(start_nodes)):
        #     rgba = color_map[start_nodes[i]]
        #     node_colors.append(rgba)

        # print(start_nodes)
        # print(color_map)

        sources = []
        targets = []
        values = []
        colors = []
        labels = []
        x = []
        y = []
        for index, row in df.iterrows():
            sources.append(nodes[row['source']])
            targets.append(nodes[row['target']])
            values.append(row['amount'])
            colors.append(row['colour'])
            labels.append(row['tag'])

        node_labels = list(nodes.keys())
        for nl in node_labels:
            x.append(positions[nl][0])
            y.append(positions[nl][1])
        print(node_labels)
        print(x)
        print(y)

        fig = go.Figure(data=[go.Sankey(
                              arrangement = 'fixed',
                              # Define nodes
                              node=dict(pad=10,
                                        thickness=15,
                                        line=dict(color="black", width=0.01),
                                        label=node_labels,
                                        x=x,
                                        y=y,
                                        # color=node_colors
                                        color="black"
                                        ),
                              # Add links
                              link=dict(source=sources,
                                        target=targets,
                                        value=values,
                                        color=colors,
                                        label=labels
                                        ))])

        fig.update_layout(title_text=title_text,
                          font=dict(size = 12, color = 'black', family = "Arial"),

                          # plot_bgcolor='#F2F2F3',  # off white
                          # paper_bgcolor='#F2F2F3',  # off white
                          # plot_bgcolor='#262626',  # black of the maps
                          # paper_bgcolor='#262626'  # black of the maps
                          # plot_bgcolor='#070D22',  # website blue
                          # paper_bgcolor='#070D22',  # website blue
                          )
        fig.show()


# test_sankey = pd.read_excel('results/testsankey.xlsx')
# test_sankey = test_sankey.groupby(['activity_group_name', 'status', 'VerwerkingsMethode'], as_index=False)['amount'].sum()
# draw_sankey(test_sankey)
