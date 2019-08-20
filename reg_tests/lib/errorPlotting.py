#
# Copyright 2017 National Renewable Energy Laboratory
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""
    This library provides tools for plotting the output channels over time of a 
    given solution attribute for two OpenFAST solutions, with the second solution
    assumed to be the baseline for comparison. There are functions for solution
    file I/O, plot creation, and html creation for navigating the plots.
"""

import sys
import os
import numpy as np
from fast_io import load_output
import rtestlib as rtl
import plotly.offline
import plotly.graph_objs as go

def _validateAndExpandInputs(argv):
    rtl.validateInputOrExit(argv, 3, "solution1 solution2 attribute")
    testSolution = argv[0]
    baselineSolution = argv[1]
    attribute = argv[2]
    rtl.validateFileOrExit(testSolution)
    rtl.validateFileOrExit(baselineSolution)
    return (testSolution, baselineSolution, attribute)

def _parseSolution(solution):
    try:
        data, info, _ = load_output(solution)
        return (data, info)
    except Exception as e:
        rtl.exitWithError("Error: {}".format(e))

def _plotError(xseries, y1series, y2series, xlabel, title1, title2, use_plotly=False):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FormatStrFormatter

    if use_plotly:
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x = xseries,
                y = y2series,
                mode = 'lines',
                line_width = 3,
                line_color = 'green',
                name = 'Baseline'
            )
        )
        fig.add_trace(
            go.Scatter(
                x = xseries,
                y = y1series,
                mode = 'lines',
                line_width = 1,
                line_color = 'red',
                name = 'Local'
            )
        )
        fig.update_layout(
            autosize = False,
            width = 550,
            height = 450,
            title_text = title1,
            titlefont = dict(size=24),
            xaxis = go.layout.XAxis(
                title_text = xlabel,
                titlefont = dict(size=18)
            )
        )
        div_string = plotly.offline.plot(fig, include_plotlyjs=False, output_type='div')
        return div_string
    else:
        plt.figure()
        plt.title(title1)
        plt.grid(True)
        plt.plot(xseries, y2series, "g", linestyle="solid", linewidth=3, label = "Baseline")
        plt.plot(xseries, y1series, "r", linestyle="solid", linewidth=1, label = "Local")
        plt.legend()
        plt.tight_layout()
        return plt

def _savePlot(plt, path, foutname):
    plt.savefig(os.path.join(path, foutname+".png"))

def plotOpenfastError(testSolution, baselineSolution, attribute, use_plotly=False):
    testSolution, baselineSolution, attribute = _validateAndExpandInputs([testSolution, baselineSolution, attribute])
    dict1, info1 = _parseSolution(testSolution)
    dict2, info2 = _parseSolution(baselineSolution)

    try:
        channel = info1['attribute_names'].index(attribute)
    except Exception as e:
        rtl.exitWithError("Error: Invalid channel name--{}".format(e))

    title1 = attribute + " (" + info1["attribute_units"][channel] + ")"
    title2 = "Max norm"
    xlabel = 'Time (s)'

    timevec = dict1[:, 0]
    y1series = np.array(dict1[:, channel], dtype = np.float)
    y2series = np.array(dict2[:, channel], dtype = np.float)

    if use_plotly:
        div_string = _plotError(timevec, y1series, y2series, xlabel, title1, title2, use_plotly=True)
        return div_string
    else:
        plt = _plotError(timevec, y1series, y2series, xlabel, title1, title2)
        basePath = os.path.sep.join(testSolution.split(os.path.sep)[:-1])
        plotPath = os.path.join(basePath, "plots")
        rtl.validateDirOrMkdir(plotPath)
        _savePlot(plt, plotPath, attribute)
        plt.close()
    
def _htmlHead(title):
    head  = '<!DOCTYPE html>' + '\n'
    head += '<html>' + '\n'
    head += '<head>' + '\n'
    head += '  <title>5MW_ITIBarge_DLL_WTurb_WavesIrr Summary</title>' + '\n'
    head += '  <script src="https://code.jquery.com/jquery-3.3.1.slim.min.js" integrity="sha384-q8i/X+965DzO0rT7abK41JStQIAqVgRVzpbzo5smXKp4YfRvH+8abtTE1Pi6jizo" crossorigin="anonymous"></script>' + '\n'
    head += '  <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.7/umd/popper.min.js" integrity="sha384-UO2eT0CpHqdSJQ6hJty5KVphtPhzWj9WO1clHTMGa3JDZwrnQq4sF86dIHNDz0W1" crossorigin="anonymous"></script>' + '\n'
    head += '  <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js" integrity="sha384-JjSmVgyd0p3pXB1rRibZUAYoIIy6OrQ6VrjIEaFf/nJGzIxFDsf4x0xIM+B07jRM" crossorigin="anonymous"></script>' + '\n'
    head += '  <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>\n'
    head += '  <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">' + '\n'
    head += '  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">\n'
    head += '  <style media="screen" type="text/css">'
    head += '    .cell-warning {'
    head += '      background-color: #FF6666;'
    head += '    }'
    head += '    .cell-highlight {'
    head += '      background-color: #E5E589;'
    head += '    }'
    head += '  </style>'
    head += '</head>' + '\n'
    return head

def _htmlTail():
    tail = '</html>' + '\n'
    return tail

def _tableHead(columns):
    head  = '    <table class="table table-bordered table-hover table-sm" style="margin: auto; width: 50%">' + '\n'
    head += '      <thead>' + '\n'
    head += '        <tr>' + '\n'
    head += '          <th>#</th>' + '\n'
    for column in columns:
        head += '          <th>{}</th>'.format(column) + '\n'
    head += '        </tr>' + '\n'
    head += '      </thead>' + '\n'
    return head

def exportResultsSummary(path, results):
    with open(os.path.join(path, "regression_test_summary.html"), "w") as html:
        
        html.write( _htmlHead("Regression Test Summary") )
        
        html.write('<body>' + '\n')
        html.write('  <h2 class="text-center">{}</h2>'.format("Regression Test Summary") + '\n')
        html.write('  <div class="container">' + '\n')
        
        # Test Case - Pass/Fail - Max Relative Norm            
        data_link = [('<a href="{0}/{0}.html">{0}</a>'.format(r[0]), r[1]) for i,r in enumerate(results)]
        data_nolink = [('{0}'.format(r[0]), r[1]) for i,r in enumerate(results)]
        table = _tableHead(['Test Case', 'Pass/Fail'])
        body = '      <tbody>' + '\n'
        for i, d in enumerate(data_link):
            body += '        <tr>' + '\n'
            body += '          <th scope="row">{}</th>'.format(i+1) + '\n'        
  
            fmt = '{0:s}'
            if (d[1] == "FAIL") and ('Linear' not in d[0]):
                body += ('          <td>' + fmt + '</td>').format(d[0]) + '\n'
                body += ('          <td class="cell-warning">' + fmt + '</td>').format(d[1]) + '\n'
            else:
                body += ('          <td>' + fmt + '</td>').format(data_nolink[i][0]) + '\n'
                body += ('          <td>' + fmt + '</td>').format(d[1]) + '\n'
                
            body += '        </tr>' + '\n'
        body += '      </tbody>' + '\n'
        table += body
        table += '    </table>' + '\n'
        html.write(table)
            
        html.write('    <br>' + '\n')
        html.write('  </div>' + '\n')
        html.write('</body>' + '\n')
        html.write( _htmlTail() )
    
def exportCombinedSummary(path, case, results, testSolution, plotList, relativeNorm, maxNorm, div_string_mat):
    with open(os.path.join(path, case+".html"), "w") as html:
      
        html.write( _htmlHead(case + " Summary") )

        html.write('<body>' + '\n')
        html.write('<h2 class="text-center">{}</h2>'.format(case + " Summary") + '\n')

        # For the summary
        data_s = [(r[0], r[1], r[2]) for i,r in enumerate(results)]

        # For the plots
        data_p = [('<input type="checkbox" name="which_graphs" value="{0}">{0}<br>'.format(plot)) for i,plot in enumerate(plotList)]     

        body = '<div class="container">\n'
        body += '<div>\n'

        body += '<form>\n'
        body += '<fieldset>\n'  
        body += '<legend>Select which graphs you would like to view:</legend>\n' 
        body += '<button class="btn btn-primary" type="button" onclick="return expandCollapseGraphs();">Expand/Collapse All Graphs <strong class="fa fa-angle-double-down"></strong></button>\n'
        body += '<br><br>\n'

        # For the buttons on top to dropdown each graph
        ncols = 5
        current_col = 0
        dc = 0
  
        for i, d in enumerate(data_s):
          
            if d[0] in plotList:
                # current_row = (i)//ncols
                current_col = (dc)%ncols
    
                if (current_col == 0):
                    body += '<div class="row">\n'
                  
                body += '<div class="col-sm">\n'
                body += '{0:s}'.format(data_p[dc])
                body += '</div>'
    
                if (current_col == (ncols-1)):
                    body += '</div>\n'
              
                dc += 1
          
        for i in range(current_col,ncols-1):
            body += '<div class="col-sm">\n'
            body += '</div>\n'

        body += '</div>\n'
        body += '<br>\n'
        body += '<button type="button" onclick="return showGraphs();">Submit</button>\n' 
        body += '</fieldset>\n'  
        body += '</form>\n'
        body += '<br>\n'

        ncols = 2

        for i, d in enumerate(data_s):
            current_row = (i)//ncols
            current_col = (i)%ncols

            if (current_col == 0):
                body += '<div class="row">\n'

            # Write the current channel button to the table
            body += '<div id="{0}{1}" class="col-sm" style="padding: 0px; height: 475px; display: none">\n'.format(current_row,current_col)
            body += '</div>\n'

            if (current_col == (ncols-1)):
                body += '</div>\n'

        if (len(div_string_mat) > 0):
            dc = 0
            for i, d in enumerate(data_s):  
                if d[0] in plotList:
                    body += '<div id="{}" name="the_graphs" style="border-style: solid; height: 475px; display: none">\n'.format(d[0])
                    body += div_string_mat[dc].replace('px','%')
                    body += '</div>\n'
                    dc += 1

        html.write(body)

        html.write('</body>' + '\n')
        html.write( _htmlTail() )

        body = ''
        body += '<script type="text/javascript">\n'  
        body += 'function showGraphs()\n'  
        body += '{\n' 
        body += '   var checkboxes = document.getElementsByName("which_graphs");\n'   
        body += '   for (var i = 0; i < checkboxes.length; i++)\n'  
        body += '   {\n'  
        body += '       if (checkboxes[i].checked)\n' 
        body += '       {\n'
        body += '           document.getElementById(checkboxes[i].value).style.display = "block";\n'
        body += '       }\n'
        body += '       else\n'
        body += '       {\n'
        body += '           document.getElementById(checkboxes[i].value).style.display = "none";\n'
        body += '       }\n'       
        body += '   }\n'
        body += '}\n'
        body += 'function expandCollapseGraphs()\n' 
        body += '{\n' 
        body += '   var all_graphs = document.getElementsByName("the_graphs");\n' 
        body += '   var num_open = 0;\n'
        body += '   for (var i = 0; i < all_graphs.length; i++)\n'  
        body += '   {\n'  
        body += '       document.getElementsByName("which_graphs")[i].checked = false;\n'
        body += '       if (all_graphs[i].style.display === "block")\n' 
        body += '       {\n'
        body += '           num_open += 1;\n'
        body += '       }\n'       
        body += '   }\n'
        body += '   if (num_open > 0)\n'
        body += '   {\n'
        body += '       for (var i = 0; i < all_graphs.length; i++)\n'  
        body += '       {\n'  
        body += '           all_graphs[i].style.display = "none";\n'   
        body += '       }\n'
        body += '   }\n'
        body += '   else\n'
        body += '   {\n'
        body += '       for (var i = 0; i < all_graphs.length; i++)\n'  
        body += '       {\n'
        body += '           document.getElementsByName("which_graphs")[i].checked = true;\n'  
        body += '           all_graphs[i].style.display = "block";\n'     
        body += '       }\n'
        body += '   }\n'
        body += '}\n'    
        body += '</script>\n'

        html.write(body)
