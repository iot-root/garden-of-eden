import { BarChartIcon, FlowerIcon, HomeIcon } from "@/icons/icons"

export const MobileNavbar = () => {
    return (
        <div class="relative w-full h-fit flex flex-row justify-center">
            <div class="flex flex-row justify-evenly max-w-[300px] w-[80%] border-solid bg-white border-[1px] border-zinc-300 rounded-full bottom-[10px] fixed p-2">
                <HomeIcon height={30} width={30} />
                <BarChartIcon height={30} width={30} />
                <FlowerIcon height={30} width={30} />
            </div>
        </div>
    )
}