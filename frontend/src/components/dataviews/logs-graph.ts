import { Colors, Legend, Title, Tooltip } from 'chart.js'
import Chart from 'chart.js/auto'
import { Line } from 'solid-chartjs'
import { createSignal, onMount, createResource, createEffect } from "solid-js"
import {Card} from "@/ui/card"
import {LogsGraph} from "@/components/dataviews/logs-graph"

export const LogsGraph = () => {

    const [chartData, setChartData] = createSignal()

    const brightnessData = [[], []]

    createEffect(() => {
        if (brightnessLogs()) {
            console.log(brightnessLogs())
            // transform text into json
            const logs = [];
            const lines = brightnessLogs().split('\n');
            
            for (const line of lines) {
                if (line.trim()) {
                    try {
                        const json = JSON.parse(line);
                        logs.push(json);
                    } catch (e) {
                        console.error('Error parsing JSON:', e, line);
                    }
                }
            }
            
            // split json data
            logs.forEach((item) => {
                brightnessData[0].push(item.timestamp)
                brightnessData[1].push(item.value)
            })            
            console.log(brightnessData)

            setChartData({
        labels: brightnessData[0],
        datasets: [
            {
                label: "Temperature \u00B0C",
                data: brightnessData[1],
                borderColor: '#FF3333', // line
                backgroundColor: '#FF3333', // dot
            },
        ],
    })
        }
    }, [brightnessLogs])

   

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
            const {ctx} = chart;
            ctx.save();
            ctx.globalCompositeOperation = 'destination-over';
            ctx.fillStyle = options.color || '#FFFFFF';
            ctx.fillRect(0, 0, chart.width, chart.height);
            ctx.restore();
        }
    }

    return (
        <Card class="w-full h-[200px] rounded-[8px] mb-4 overflow-hidden">
            <Line data={chartData()} options={chartOptions} width={500} height={500} plugins={plugin}/>
        </Card>
    )
}