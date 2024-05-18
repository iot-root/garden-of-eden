import { H1 } from "@/typography/heading"
import Padding from "../containers/padding"
import { Add } from "../ui/add"
import { Dot } from "../ui/dot"

export const Log = () => {
    return (
        <Padding>
            <div class="flex flex-row justify-between items-center mb-4">
                <H1 >Log</H1>
                <Add label="Create" />
            </div>

            <div class="w-full h-[200px] bg-zinc-200 rounded-[8px] mb-4">

            </div>

            {/* Legend */}
            <div>
                {/* row */}
                <div class="flex flex-row justify-between">
                    {/* item */}
                    <div class="flex flex-row justify-between items-center w-[100px]">
                        {/* text */}
                        <p class="text-zinc-400 text-sm w-min mr-4">Temp</p>
                        {/* dot */}
                        <Dot class="bg-red-500"></Dot>
                    </div>

                    <div class="flex flex-row justify-between items-center w-[100px]">
                        {/* text */}
                        <p class="text-zinc-400 text-sm w-min mr-4">Lights</p>
                        {/* dot */}
                        <Dot class="bg-yellow-500"></Dot>
                    </div>

                    <div class="flex flex-row justify-between items-center w-[100px]">
                        {/* text */}
                        <p class="text-zinc-400 text-sm w-min mr-4">Water</p>
                        {/* dot */}
                        <Dot class="bg-blue-500"></Dot>
                    </div>

                </div>
                <div class="flex flex-row justify-between">
                    {/* item */}
                    <div class="flex flex-row justify-between items-center w-[100px]">
                        {/* text */}
                        <p class="text-zinc-400 text-sm w-min mr-4">Humidity</p>
                        {/* dot */}
                        <Dot class="bg-green-500"></Dot>
                    </div>

                    <div class="flex flex-row justify-between items-center w-[100px]">
                        {/* text */}
                        <p class="text-zinc-400 text-sm w-min mr-4">PCB</p>
                        {/* dot */}
                        <Dot class="bg-orange-500"></Dot>
                    </div>

                    <div class="flex flex-row justify-between items-center w-[100px]">
                        {/* text */}
                        <p class="text-zinc-400 text-sm w-min mr-4">Pump</p>
                        {/* dot */}
                        <Dot class="bg-zinc-400"></Dot>
                    </div>

                </div>

            </div>
        </Padding>
    )
}