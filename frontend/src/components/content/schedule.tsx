import Padding from "@/components/containers/padding"
import { Add } from "@/components/ui/add"
import { Settings } from "@/icons/icons"
import data from "@/root/data.json"
import { H1, P } from "@/typography/heading"
import { Card } from "@/ui/card"

export const Schedule = () => {
    return (
        <Padding>
            <div class="flex flex-row justify-between items-center mb-4">
                <H1 class="w-min">Schedule</H1>
                <Add label="Create" />
            </div>

            <Card>
                {Object.entries(data.schedules).map((e) => {
                    return (
                        <div class="flex flex-col items-start mb-4">
                            {/* sensor */}
                            <p class="capitalize font-medium">{e[0]}</p>

                            <div class="flex flex-col justify-between w-full">

                                {Object.entries(e[1]).map((s) => {
                                    return (
                                        <div class="w-full flex flex-row justify-between items-center">
                                            <P class="text-zinc-400 text-sm">{s[1].day},  {s[1].time} -  {s[1].property.name} -  {s[1].property.value}</P>
                                            <Settings height={30} width={30} />
                                        </div>
                                    )
                                })}
                            </div>
                        </div>
                    )
                })}
            </Card>
        </Padding>
    )
}