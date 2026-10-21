import numpy
import matplotlib
import matplotlib.pyplot

class PlotFieldMap:
    def __init__(self):
        pass

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

    def plot_field_map(self):
        figure = matplotlib.pyplot.figure()
        axes = figure.add_subplot(1, 1, 1)
        x_space = numpy.linspace(-2.01, 2.01, 202)
        z_space = numpy.linspace(-2.01, 2.01, 202)
        print(x_space)
        cmax = max([abs(by) for by in self.by_list])
        h = axes.hist2d(self.x_list, self.z_list, weights=self.by_list, bins=[x_space, z_space], cmap="coolwarm", vmin=-cmax, vmax=cmax)
        figure.colorbar(h[3])


def main():
    plotter = PlotFieldMap()
    plotter.load_field_map()
    plotter.plot_field_map()

if __name__ == "__main__":
    main()
    matplotlib.pyplot.show(block=False)
    input("Press <CR> to finish")
