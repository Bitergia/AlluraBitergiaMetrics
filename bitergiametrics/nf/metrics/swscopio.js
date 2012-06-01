function displayEvoTickets(id, datafile) {

	var container = document.getElementById(id);

	$.getJSON(datafile, function(history) {

		var data, options, i;

		// Data Format:
		data = [ [ history.id, history.tickets ] ];

		// TimeSeries Template Options
		options = {
			// Container to render inside of
			container : container,
			// Data for detail (top chart) and summary (bottom chart)
			data : {
				detail : data,
				summary : data
			},
			// Initial selection
			selection : {
				data : {
					x : {
						min : history.id[0],
						max : history.id[history.month.length - 1]
					}
				}
			}
		};

		// Create the TimeSeries
		new envision.templates.TimeSeries(options);
	});
}

// Display timeseries for commits and committers using
// the finance envision template
function displayEvoCommits(id, datafile) {

	var container = document.getElementById(id);

	$.getJSON(datafile,
			function(history) {

				var V = envision, firstMonth = history.id[0], commits = [
						history.id, history.commits ], committers = [
						history.id, history.committers ], ratio = [ history.id,
						history.ratio ], dates = history.date, options, vis;

				options = {
					container : container,
					data : {
						price : commits,
						volume : committers,
						summary : commits
					},
					trackFormatter : function(o) {

						var
						// index = o.index,
						data = o.series.data, index = data[o.index][0]
								- firstMonth, value;

						value = dates[index] + ": " + commits[1][index]
								+ " commits, " + committers[1][index]
								+ " committers (commits per committer: "
								+ ratio[1][index] + ")";

						return value;
					},
					xTickFormatter : function(index) {
						return Math.floor(index / 12) + '';
					},
					yTickFormatter : function(n) {
						return n + '';
					},
					// Initial selection
					selection : {
						data : {
							x : {
								min : history.id[0],
								max : history.id[history.id.length - 1]
							}
						}
					}
				};

				// Create the TimeSeries
				vis = new envision.templates.Finance(options);
			});
}

// Display timeseries for commits/committers ratio
// using the timeseries envision template
function displayCommitsRatio(id, datafile) {

	var container = document.getElementById(id);

	$.getJSON(datafile, function(history) {

		var data, options, i;

		// Data Format:
		data = [ [ history.id, history.ratio ] ];

		// TimeSeries Template Options
		options = {
			// Container to render inside of
			container : container,
			// Data for detail (top chart) and summary (bottom chart)
			data : {
				detail : data,
				summary : data
			},
			// Initial selection
			selection : {
				data : {
					x : {
						min : history.id[0],
						max : history.id[history.month.length - 1]
					}
				}
			}
		};

		// Create the TimeSeries
		new envision.templates.TimeSeries(options);
	});
}

// Display timeseries for commits and committers using
// the finance envision template
function displayEvoLines(id, datafile, show) {

	var container = document.getElementById(id);
	container.innerHTML = "";

	$
			.getJSON(
					datafile,
					function(history) {

						var V = envision, firstMonth = history.id[0], commits = [
								history.id, history.commits ], added = [
								history.id, history.added ], removed = [
								history.id, history.removed ], ratio = [
								history.id, history.ratio ], dates = history.date, options, vis;

						if (show == "removed") {
							price = removed
						} else if (show == "added") {
							price = added
						} else if (show == "added,removed") {
							price = [ added, removed ]
						} else {
							price = [ added, removed ]
						}
						options = {
							container : container,
							data : {
								price : price,
								volume : ratio,
								summary : commits
							},
							trackFormatter : function(o) {

								var data = o.series.data, index = data[o.index][0]
										- firstMonth, value;

								value = dates[index] + ' (' + commits[1][index]
										+ " commits): ";
								if (show == "removed") {
									value += removed[1][index]
											+ " lines removed, "
								} else if (show == "added") {
									value += added[1][index] + " lines added, "
								} else if (show == "added,removed") {
									value += added[1][index] + " lines added, "
											+ removed[1][index] + " removed, "
								} else {
									value += added[1][index] + " lines added, "
											+ removed[1][index] + " removed, "
								}

								value += ratio[1][index]
										+ " lines changed / commit";

								// value = dates[index] + ' (' +
								// commits[1][index] + " commits): " +
								// added[1][index] + " lines added, " +
								// ratio[1][index] + " lines changed / commit";

								return value;
							},
							xTickFormatter : function(index) {
								return Math.floor(index / 12) + '';
							},
							yTickFormatter : function(n) {
								return n + '';
							},
							// Initial selection
							selection : {
								data : {
									x : {
										min : history.id[0],
										max : history.id[history.month.length - 1]
									}
								}
							}
						};

						// Create the TimeSeries
						vis = new envision.templates.Finance(options);
					});
}
