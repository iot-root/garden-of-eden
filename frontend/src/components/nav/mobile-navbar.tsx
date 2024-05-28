import { BarChart, Camera, Flower, Home } from '@/icons/icons';
import { A, useLocation } from '@solidjs/router';

export const MobileNavbar = () => {
  return (
    <div class="md:hidden w-full h-fit flex flex-row justify-center relative">
      <div class="flex flex-row justify-evenly max-w-[300px] w-[80%] border-solid bg-white border-[1px] border-zinc-300 rounded-full bottom-[10px] fixed p-2">
        <A href="/">
          <Home
            height={30}
            width={30}
            selected={useLocation().pathname === '/' ? true : false}
          />
        </A>

        <A href="/logs">
          <BarChart
            height={30}
            width={30}
            selected={useLocation().pathname === '/logs' ? true : false}
          />
        </A>

        <A href="/camera">
          <Camera
            height={30}
            width={30}
            selected={useLocation().pathname === '/camera' ? true : false}
          />
        </A>

        <A href="/notifications">
          <Flower
            height={30}
            width={30}
            selected={
              useLocation().pathname === '/notifications' ? true : false
            }
          />
        </A>
      </div>
    </div>
  );
};
