import { Card } from '@/ui/card'
import { Colors, Legend, Title, Tooltip } from 'chart.js'
import Chart from 'chart.js/auto'
import { Line } from 'solid-chartjs'
import { createSignal, onMount } from "solid-js"

export const LineGraph = (props) => {
    const [chartData, setChartData] = createSignal()

    setChartData({
        labels: props.labels,
        datasets: [
            {
                label: props.title,
                data: props.data,
                borderColor: '#FF3333', // line
                backgroundColor: '#FF3333', // dot
            },
        ],
    })


    onMount(() => {
        Chart.register(Title, Tooltip, Legend, Colors)
    })

    const chartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            customCanvasBackgroundColor: {
                color: '#FFFFFF',
            },
            legend: {
                labels: {
                    usePointStyle: true, // Use point style for legend
                    pointStyle: 'circle', // Set point style to 'circle'
                    boxWidth: 5,
                    boxHeight: 5,
                }
            }
        }
    }

    const plugin = {
        id: 'customCanvasBackgroundColor',
        beforeDraw: (chart, args, options) => {
            const { ctx } = chart;
            ctx.save();
            ctx.globalCompositeOperation = 'destination-over';
            ctx.fillStyle = options.color || '#FFFFFF';
            ctx.fillRect(0, 0, chart.width, chart.height);
            ctx.restore();
        }
    }

    return (
        <Card class="h-[200px] rounded-[8px] mb-4 overflow-hidden">
            <Line data={chartData()} options={chartOptions} height={500} plugins={plugin} />
        </Card>
    )
}