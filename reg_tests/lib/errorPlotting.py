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

    if (use_plotly is True):

      fig = go.Figure()

      fig.add_trace(go.Scatter(x = xseries, y = y2series,
                    mode = 'lines',
                    line_width = 3,
                    line_color = 'green',
                    name = 'Baseline'
                    )
      )

      fig.add_trace(go.Scatter(x = xseries, y = y1series,
                    mode = 'lines',
                    line_width = 1,
                    line_color = 'red',
                    name = 'Local'
                    )
      )
      
      fig.update_layout(
        autosize = False,
        width = 1000,
        height = 500,
        title_text = title1,
        titlefont = dict(size=24),
        xaxis = go.layout.XAxis(
          title_text = xlabel,
          titlefont = dict(size=24)
        )
      )

      div_string = plotly.offline.plot(fig, include_plotlyjs=False, output_type='div')

      return div_string

    else:

      plt.figure()

      # ax = plt.subplot(211)
      plt.title(title1)
      plt.grid(True)
      plt.plot(xseries, y2series, "g", linestyle="solid", linewidth=3, label = "Baseline")
      plt.plot(xseries, y1series, "r", linestyle="solid", linewidth=1, label = "Local")
      plt.legend()
      
      # ax = plt.subplot(212)
      # plt.title(title2)
      # plt.grid(True)
      # plt.plot(xseries, abs(y2series - y1series))
      # plt.xlabel(xlabel)
      # ax.yaxis.set_major_formatter(FormatStrFormatter('%.1e'))
      
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

    if (use_plotly is True):

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
    head += '  <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">' + '\n'
    head += '  <style media="screen" type="text/css">    .cell-warning {      background-color: #FF6666;    }    .cell-highlight {      background-color: #E5E589;    }  </style>' + '\n'
    head += '  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">\n'
    head += '  <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>\n'
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
    
def initializePlotDirectory(testSolution, plotList, relativeNorm, maxNorm):
    basePath = os.path.sep.join(testSolution.split(os.path.sep)[:-1])
    plotPath = os.path.join(basePath, "plots")
    caseName = basePath.split(os.path.sep)[-1]
    rtl.validateDirOrMkdir(plotPath)
    
    with open(os.path.join(plotPath, "plots.html"), "w") as html:
        
        html.write( _htmlHead(caseName) )
        
        html.write('<body>' + '\n')
        html.write('  <h2 class="text-center">{}</h2>'.format(caseName) + '\n')
        html.write('  <div class="container">' + '\n')
        html.write('  <h4 class="text-center">Maximum values for each norm are highlighted</h2>' + '\n')
        
        # Channel - Relative Norm - Max Norm
        data = [('<a href="#{0}">{0}</a>'.format(plot), relativeNorm[i], maxNorm[i]) for i,plot in enumerate(plotList)]    
        maxRelNorm = max(relativeNorm)
        maxMaxNorm = max(maxNorm)
        table = _tableHead(['Channel', 'Relative Max Norm', 'Infinity Norm'])
        body = '      <tbody>' + '\n'
        for i, d in enumerate(data):
            body += '        <tr>' + '\n'
            body += '          <th scope="row">{}</th>'.format(i+1) + '\n'
            body += '          <td>{0:s}</td>'.format(d[0]) + '\n'
            
            fmt = '{0:0.4e}'
            if d[1] == maxRelNorm:
                body += ('          <td class="cell-highlight">' + fmt + '</td>').format(d[1]) + '\n'
            else:
                body += ('          <td>' + fmt + '</td>').format(d[1]) + '\n'
                    
            if d[2] == maxMaxNorm:
                body += ('          <td class="cell-highlight">' + fmt + '</td>').format(d[2]) + '\n'
            else:
                body += ('          <td>' + fmt + '</td>').format(d[2]) + '\n'
            body += '        </tr>' + '\n'
        body += '      </tbody>' + '\n'
        table += body
        table += '    </table>' + '\n'
        html.write(table)
        
        html.write('    <br>' + '\n')
        html.write('    <div class="row">' + '\n')
        for i,plot in enumerate(plotList):
            html.write('      <div id={} class="col-sm-12 col-md-6 col-lg-6">'.format(plot) + '\n')
            html.write('        <img src="{}" class="center-block img-responsive thumbnail">'.format(plot+".png") + '\n')
            html.write('      </div>' + '\n')
        html.write('    </div>' + '\n')
        html.write('  </div>' + '\n')
        html.write('</body>' + '\n')
        html.write( _htmlTail() )
    html.close()
    
def exportResultsSummary(path, results):
    print(results)
    with open(os.path.join(path, "regression_test_summary.html"), "w") as html:
        
        html.write( _htmlHead("Regression Test Summary") )
        
        html.write('<body>' + '\n')
        html.write('  <h2 class="text-center">{}</h2>'.format("Regression Test Summary") + '\n')
        html.write('  <div class="container">' + '\n')
        
        # Test Case - Pass/Fail - Max Relative Norm            
        data = [('<a href="{0}/{0}.html">{0}</a>'.format(r[0]), r[1]) for i,r in enumerate(results)]
        table = _tableHead(['Test Case', 'Pass/Fail'])
        body = '      <tbody>' + '\n'
        for i, d in enumerate(data):
            body += '        <tr>' + '\n'
            body += '          <th scope="row">{}</th>'.format(i+1) + '\n'
            body += '          <td>{0:s}</td>'.format(d[0]) + '\n'
            
            fmt = '{0:s}'
            if d[1] == "FAIL":
                body += ('          <td class="cell-warning">' + fmt + '</td>').format(d[1]) + '\n'
            else:
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
    html.close()
    
def exportCaseSummary(path, case, results):
    with open(os.path.join(path, case+".html"), "w") as html:
        
        html.write( _htmlHead(case + " Summary") )
        
        html.write('<body>' + '\n')
        html.write('  <h2 class="text-center">{}</h2>'.format(case + " Summary") + '\n')
        html.write('  <h4 class="text-center"><a href="plots/plots.html">Go To Plots</a></h4>' + '\n')
        html.write('  <h4 class="text-center">Maximum values for each norm are highlighted</h4>' + '\n')
        html.write('  <div class="container">' + '\n')
        
        # Channel - Relative Norm - Max Norm
        data = [(r[0], r[1], r[2]) for i,r in enumerate(results)]
        maxRelNorm = max([r[1] for i,r in enumerate(results)])
        maxMaxNorm = max([r[2] for i,r in enumerate(results)])
        table = _tableHead(['Channel', 'Relative Max Norm', 'Infinity Norm'])
        body = '      <tbody>' + '\n'
        for i, d in enumerate(data):
            body += '        <tr>' + '\n'
            body += '          <th scope="row">{}</th>'.format(i+1) + '\n'
            body += '          <td>{0:s}</td>'.format(d[0]) + '\n'
            
            fmt = '{0:0.4e}'
            if d[1] == maxRelNorm:
                body += ('          <td class="cell-highlight">' + fmt + '</td>').format(d[1]) + '\n'
            else:
                body += ('          <td>' + fmt + '</td>').format(d[1]) + '\n'
                    
            if d[2] == maxMaxNorm:
                body += ('          <td class="cell-highlight">' + fmt + '</td>').format(d[2]) + '\n'
            else:
                body += ('          <td>' + fmt + '</td>').format(d[2]) + '\n'
            body += '        </tr>' + '\n'
        body += '      </tbody>' + '\n'
        table += body
        table += '    </table>' + '\n'
        html.write(table)
        
        html.write('    <br>' + '\n')
        html.write('  </div>' + '\n')
        html.write('</body>' + '\n')
        html.write( _htmlTail() )
    html.close()

def exportCombinedSummary(path, case, results, testSolution, plotList, relativeNorm, maxNorm, div_string_mat):
  """
  testSolution, plotList, relativeNorm, maxNorm
  path, case, results
  """
  with open(os.path.join(path, case+".html"), "w") as html:
      
    html.write( _htmlHead(case + " Summary") )
    
    html.write('<body>' + '\n')
    html.write('  <h2 class="text-center">{}</h2>'.format(case + " Summary") + '\n')
    
    # Channel - Relative Norm - Max Norm
    # For the summary
    data_s = [(r[0], r[1], r[2]) for i,r in enumerate(results)]

    # For the plots
    data_p = [('<button type="button" class="btn btn-info btn-lg" data-toggle="collapse" data-target="#{0}">{0} <strong class="fa fa-angle-double-down"></strong></button>'.format(plot), relativeNorm[i], maxNorm[i]) for i,plot in enumerate(plotList)]    

    # table = _tableHead(['Channel', 'Relative Max Norm', 'Infinity Norm'])
    body = '  <div class="container">\n'
    body += '  <button class="btn btn-primary" type="button" data-toggle="collapse" data-target=".multi-collapse">Expand/Collapse All Graphs <strong class="fa fa-angle-double-down"></strong></button>\n'
    body += '  <br><br>\n'
    body += '    <div>\n'

    # For the buttons on top to dropdown each graph
    ncols = 5

    for i, d in enumerate(data_s):
      # current_row = (i)//ncols
      current_col = (i)%ncols
      
      if (current_col == 0):
        body += '      <div class="row">\n'
      
      body += '        <div class="col-sm">\n'
      body += '{0:s}'.format(data_p[i][0])
      body += '        </div>'
      
      if (current_col == (ncols-1)):
        body += '      </div>\n'
    
    for i in range(current_col,ncols-1):
      body += '      <div class="col-sm">\n'
      body += '      </div>\n'

    body += '    </div>\n'
    body += '  <br>\n'

    # For the containers used to hold the graphs
    ncols = 1

    for i, d in enumerate(data_s):
      # current_row = (i)//ncols
      current_col = (i)%ncols
      # fmt = '{0:0.4e}'

      # Write the current channel button to the table
      body += '        <div class="col-sm" style="padding: 0px; height: 500px;">\n'

      body += '          <div id="{}" class="collapse multi-collapse" style="border-style: solid; height: 500px;">\n'.format(d[0])

      body += div_string_mat[i].replace('px','%')
      body += '          </div>\n'

    body += '  </div>\n'
    html.write(body)

    html.write('</body>' + '\n')
    html.write( _htmlTail() )

  html.close()

