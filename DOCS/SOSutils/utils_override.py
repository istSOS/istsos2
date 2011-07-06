
def legend(*args, **kwargs):
    from matplotlib import pylab
    """
    Overwrites the pylab legend function.

    It adds another location identfier 'outer right'
    which locates the legend on the right side of the plot

    The args and kwargs are forwarded to the pylab legend function
    """
    if kwargs.has_key('loc'):
        loc = kwargs['loc']
        loc = loc.split()

        if loc[0] == 'outer':
            # make a legend with out the location
            # remove the location setting from the kwargs
            kwargs.pop('loc')
            leg = pylab.legend(loc=(0,0), *args, **kwargs)
            frame = leg.get_frame()
            currentAxes = pylab.gca()
            currentAxesPos = currentAxes.get_position()
            # scale plot by the part which is taken by the legend
            plotScaling = frame.get_width()/currentAxesPos[2]

            if loc[1] == 'right':
                # scale the plot
                currentAxes.set_position((currentAxesPos[0], currentAxesPos[1],
                                          currentAxesPos[2] * (1-plotScaling),
                                          currentAxesPos[3]))
                # set x and y coordinates of legend
                leg._loc = (1 + leg.axespad, 1 - frame.get_height())

            # doesn't work
            #if loc[1] == 'left':
            #    # scale the plot
            #    currentAxes.set_position((currentAxesPos[0] + frame.get_width(),
            #                              currentAxesPos[1],
            #                              currentAxesPos[2] * (1-plotScaling),
            #                              currentAxesPos[3]))
            #    # set x and y coordinates of legend
            #    leg._loc = (1 -.05 -  leg.axespad - frame.get_width(), 1 - frame.get_height())

            pylab.draw_if_interactive()
            return leg

    return pylab.legend(*args, **kwargs)

