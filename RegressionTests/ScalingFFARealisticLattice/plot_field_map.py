import glob

import numpy
import matplotlib
import matplotlib.pyplot

class PlotFieldMap:
    def __init__(self):
        self.x_list, self.z_list, self.by_list = [], [], []
        self.beam_x_list, self.beam_z_list = [], []

    def load(self):
        self.load_field_map()
        self.load_beam()

    def load_field_map(self):
        filename = "data/map.dat"
        fin = open(filename)
        for i in range(12):
            fin.readline()
        self.x_list, self.z_list, self.by_list = [], [], []
        for line in fin.readlines():
            words = [float(x) for x in line.split()]
            self.x_list.append(words[0])
            self.z_list.append(words[2])
            self.by_list.append(words[5])

    def load_beam(self):
        beamname = glob.glob("data/*_DesignPath.dat")[0]
        beamfile = open(beamname)
        beamfile.readline() # header
        for line in beamfile.readlines():
            words = line.split()
            self.beam_x_list.append(float(words[1]))
            self.beam_z_list.append(float(words[3]))

    def plot_field_map(self):
        figure = matplotlib.pyplot.figure()
        axes = figure.add_subplot(1, 1, 1)
        x_space = numpy.linspace(-9.01, 1.01, 202)
        z_space = numpy.linspace(-5.01, 5.01, 202)
        cmax = max([abs(by) for by in self.by_list])
        h = axes.hist2d(self.x_list, self.z_list, weights=self.by_list, bins=[x_space, z_space], cmap="coolwarm", vmin=-cmax, vmax=cmax)
        figure.colorbar(h[3])

        beam_h = axes.plot(self.beam_x_list, self.beam_z_list)



def main():
    plotter = PlotFieldMap()
    plotter.load()
    plotter.plot_field_map()

if __name__ == "__main__":
    main()
    matplotlib.pyplot.show(block=False)
    input("Press <CR> to finish")
