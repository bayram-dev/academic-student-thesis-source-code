all: ping.dat ping.png plot

ping.dat:
	sudo python main.py

plot: iperf3.json
	plot_iperf.sh iperf3.json

ping.png: ping.dat
	gnuplot ping_plot

clean:
	-rm -f *.dat *.pdf *.json *.csv
	-rm -rf results
	sudo mn -c
