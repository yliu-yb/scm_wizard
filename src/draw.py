from mplwidget import MplCanvas
from datetime import timedelta
import matplotlib.dates as mdates
import datetime
import numpy
from numpy import ma
from matplotlib import ticker

def fmt(x, pos):
    a, b = '{:.0e}'.format(x).split('e')
    b = int(b)
    return r'$10^{{{}}}$'.format(b)

def draw_wrfout(canvas : MplCanvas, x, y, data, xlabel, ylabel, title, barlabel):
    data = list(map(list, zip(*data)))
    ax1 = canvas.fig.add_subplot(111)
    if x[len(x) - 1] - x[0] > timedelta(days=1):
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m%d'))
    else:
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H%M'))
    ax1.set_ylim(top=12)

    cs = ax1.contourf(x, y, data, cmap='jet')
    cbar = canvas.fig.colorbar(cs, ax=ax1, pad=0.01, label=barlabel)
    ax1.set_title(title)
    ax1.set_xlabel(xlabel)
    ax1.set_ylabel(ylabel)
    canvas.fig.autofmt_xdate()
    canvas.fig.set_tight_layout(True)
    canvas.draw()
    cbar.remove()
    ax1.remove()

def draw_force(canvas : MplCanvas, f_datetime, f_z, f_variable_2D, title, ylabel, xlabel, cbar_label, log_mk=False):
    force_datetime = [datetime.datetime.strptime(dt, '%Y-%m-%d_%H:%M:%S') for dt in f_datetime]
    f_variable_2D = list(map(list, zip(*f_variable_2D)))
    ax1 = canvas.fig.add_subplot(111)
    if force_datetime[len(force_datetime) - 1] - force_datetime[0] > timedelta(days=1):
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m%d'))
    else:
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H%M'))
    ax1.set_ylim(top=12)
    if log_mk:
        f_variable_2D = numpy.array(f_variable_2D)
        f_variable_2D = ma.masked_where(f_variable_2D <= 0, f_variable_2D)
        cs = ax1.contourf(force_datetime, f_z, f_variable_2D, locator=ticker.LogLocator(), cmap='jet')
        # cntr1, ax = ax0, pad = 0.01, format = ticker.FuncFormatter(fmt)
        cbar = canvas.fig.colorbar(cs, ax=ax1, pad=0.01, format=ticker.FuncFormatter(fmt),
                                                             label=cbar_label)
    else:
        cs = ax1.contourf(force_datetime, f_z, f_variable_2D, cmap='jet')
        cbar = canvas.fig.colorbar(cs, ax=ax1, pad=0.01, label=cbar_label)
    ax1.set_title(title)
    ax1.set_xlabel(xlabel)
    ax1.set_ylabel(ylabel)
    canvas.fig.autofmt_xdate()
    canvas.fig.set_tight_layout(True)
    canvas.draw()
    cbar.remove()
    ax1.remove()

def draw_initialization(canvas : MplCanvas, souding_z, souding_qv, souding_theta, souding_u, souding_v):
    sounding_z = [x / 1000 for x in souding_z]
    gs = canvas.fig.add_gridspec(1, 4)

    ax1 = canvas.fig.add_subplot(gs[0,0:3])
    ax2 = canvas.fig.add_subplot(gs[0,3:4])
    #
    sounding_qv = numpy.array(souding_qv)
    sounding_qv = ma.masked_where(sounding_qv <= 0, sounding_qv)
    ax1.set_xscale('log')
    ax1.set_ylim(top = 12)
    p1, = ax1.plot(sounding_qv, sounding_z, 'b-', label = 'qv')
    ax1.set_xlabel('kgkg$^{-1}$')
    ax1.set_ylabel('Height(km)')
    ax1.xaxis.label.set_color(p1.get_color())
    ax11 = ax1.twiny()
    p11, = ax11.plot(souding_theta, sounding_z, 'g-', label = 'theta')
    ax11.set_xlabel('K')
    ax11.xaxis.label.set_color(p11.get_color())
    tkw = dict(size=4, width=1.5)
    ax1.tick_params(axis='x', colors=p1.get_color(), **tkw)
    ax11.tick_params(axis='x', colors=p11.get_color(), **tkw)
    ax1.legend(handles=[p1, p11])
    ax2.set_ylim(top = 12)
    ax2.barbs([0 for x in range(len(sounding_z))], sounding_z, souding_u, souding_v, length = 7)
    ax2.set_title('Wind')
    ax2.axes.get_xaxis().set_visible(False)
    # ax2.axes.get_yaxis().set_visible(False)
    canvas.fig.set_tight_layout(True)
    canvas.draw()
    ax1.remove()
    ax11.remove()
    ax2.remove()