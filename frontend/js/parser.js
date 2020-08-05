
(function(){

    parse = function(attachment){
        // Call the function assigned to this particular kind of answer.
        // Check out the var types at the end of this file.
        return funs[attachment.contentType](attachment.content);
    };

    // local functions
    var parse_question = function(content){
        return '<i>' + content + '</i>';
    };

    var parse_feedback = function(content){
        return '<font color="green">' + content + '</font>';
    };

    var parse_text = function(content){
        return content.autoLink === 'function' ?
                    content.autoLink() : content;
    };

    var parse_list = function(content){
        return '<ol>' +
               content.map(element => '<li>' + element + '</li>').join('\n') +
               '</ol>';
    };

    var parse_youtube = function(content){
        return '<iframe width="100%" height="315" src="' + content +
               '" frameborder="0" allowfullscreen></iframe>';
    }
    // doc at http://www.chartjs.org/docs/#getting-started-usage
    var parse_histogram = function(content){
        // put the canvas in the chat
        var canvasId = 'histogram_' + (Math.random());
        var canvasHtml = $('<div><canvas id="' + canvasId + '" style="width:100%; height:100%;"></canvas></div>').appendTo('body');

        // draw chart in canvas
        var ctx = document.getElementById(canvasId);
        var myChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: content.labels,
                datasets: [{
                    label: '# of Votes',
                    data: content.values,
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.2)',
                        'rgba(54, 162, 235, 0.2)',
                        'rgba(255, 206, 86, 0.2)',
                        'rgba(75, 192, 192, 0.2)',
                        'rgba(153, 102, 255, 0.2)',
                        'rgba(255, 159, 64, 0.2)'
                    ],
                    borderColor: [
                        'rgba(255,99,132,1)',
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 206, 86, 1)',
                        'rgba(75, 192, 192, 1)',
                        'rgba(153, 102, 255, 1)',
                        'rgba(255, 159, 64, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    yAxes: [{
                        ticks: {
                            beginAtZero:true
                        }
                    }]
                }
            }
        });
        return canvasHtml;
    }
    // doc at http://www.chartjs.org/docs/#getting-started-usage
    var parse_piechart = function(content){
        // put the canvas in the chat
        var canvasId = 'pieChart_' + (Math.random());
        var canvasHtml = $('<div><canvas id="' + canvasId + '" style="width:100%; height:100%;"></canvas></div>').appendTo('body');

        // draw chart in canvas
        var ctx = document.getElementById(canvasId);
        var myChart = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: content.labels,
                datasets: [{
                    data: content.values,
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.2)',
                        'rgba(54, 162, 235, 0.2)',
                        'rgba(255, 206, 86, 0.2)',
                        'rgba(75, 192, 192, 0.2)',
                        'rgba(153, 102, 255, 0.2)',
                        'rgba(255, 159, 64, 0.2)'
                    ],
                    borderColor: [
                        'rgba(255,99,132,1)',
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 206, 86, 1)',
                        'rgba(75, 192, 192, 1)',
                        'rgba(153, 102, 255, 1)',
                        'rgba(255, 159, 64, 1)'
                    ],
                    borderWidth: 1
                }]
            }
        });
        return canvasHtml;
    }

    var funs = {
        'question' : parse_question,
        'feedback': parse_feedback,
        'text' : parse_text,
        'list' : parse_list,
        'youtube': parse_youtube,
        'histogram': parse_histogram,
        'pie': parse_piechart
    };

})();
