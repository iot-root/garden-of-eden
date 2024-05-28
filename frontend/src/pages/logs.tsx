import { Logs } from '@/components/content/logs';
import { useNavigate } from '@solidjs/router';
import { createEffect } from 'solid-js';

export default () => {
  const navigate = useNavigate();

  createEffect(() => {
    const handleResize = () => {
      if (window.innerWidth >= 768) {
        navigate('/');
      }
    };

    window.addEventListener('resize', handleResize);

    handleResize();

    return () => {
      window.removeEventListener('resize', handleResize);
    };
  });

  return (
    <div class="w-full md:w-[80%]">
      <Logs />
    </div>
  );
};
