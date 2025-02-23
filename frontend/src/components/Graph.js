import React from 'react';
import { Line } from 'react-chartjs-2';

function Graph({ data }) {
  const chartData = {
    labels: data.map(point => point.label),
    datasets: [
      {
        label: 'Performance',
        data: data.map(point => point.value),
        fill: false,
        backgroundColor: 'blue',
        borderColor: 'blue',
      },
    ],
  };

  return <Line data={chartData} />;
}

export default Graph;