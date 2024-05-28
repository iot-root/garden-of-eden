export const Home = (props) => {
  return (
    <svg
      fill="none"
      height={props.height}
      viewBox="0 0 41 41"
      width={props.width}
      xmlns="http://www.w3.org/2000/svg"
    >
      <g
        stroke={props.selected ? '#000' : '#D1D1D1'}
        stroke-linecap="round"
        stroke-linejoin="round"
        stroke-width="2"
      >
        <path d="m5.125 15.3751 15.375-11.95835 15.375 11.95835v18.7916c0 .9062-.36 1.7752-1.0007 2.416-.6408.6407-1.5098 1.0007-2.416 1.0007h-23.91663c-.90616 0-1.7752-.36-2.41595-1.0007-.64075-.6408-1.00072-1.5098-1.00072-2.416z" />
        <path d="m15.375 37.5833v-17.0833h10.25v17.0833" />
      </g>
    </svg>
  );
};

export const Flower = (props) => {
  return (
    <svg
      width={props.width}
      height={props.height}
      viewBox="0 0 41 41"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        d="M20.5 12.8125C20.5 11.2921 20.9509 9.80576 21.7956 8.54156C22.6403 7.27735 23.8409 6.29203 25.2456 5.71018C26.6503 5.12833 28.196 4.97609 29.6873 5.27272C31.1785 5.56934 32.5483 6.3015 33.6234 7.37662C34.6985 8.45174 35.4307 9.82152 35.7273 11.3127C36.0239 12.804 35.8717 14.3497 35.2898 15.7544C34.708 17.1591 33.7227 18.3597 32.4585 19.2044C31.1942 20.0491 29.7079 20.5 28.1875 20.5M20.5 12.8125C20.5 11.2921 20.0491 9.80576 19.2044 8.54156C18.3597 7.27735 17.1591 6.29203 15.7544 5.71018C14.3497 5.12833 12.804 4.97609 11.3127 5.27272C9.82152 5.56934 8.45174 6.3015 7.37662 7.37662C6.3015 8.45174 5.56934 9.82152 5.27272 11.3127C4.97609 12.804 5.12833 14.3497 5.71018 15.7544C6.29203 17.1591 7.27735 18.3597 8.54156 19.2044C9.80576 20.0491 11.2921 20.5 12.8125 20.5M20.5 12.8125V15.375M28.1875 20.5C29.7079 20.5 31.1942 20.9509 32.4585 21.7956C33.7227 22.6403 34.708 23.8409 35.2898 25.2456C35.8717 26.6503 36.0239 28.196 35.7273 29.6873C35.4307 31.1785 34.6985 32.5483 33.6234 33.6234C32.5483 34.6985 31.1785 35.4307 29.6873 35.7273C28.196 36.0239 26.6503 35.8717 25.2456 35.2898C23.8409 34.708 22.6403 33.7227 21.7956 32.4585C20.9509 31.1942 20.5 29.7079 20.5 28.1875M28.1875 20.5H25.625M12.8125 20.5C11.2921 20.5 9.80576 20.9509 8.54156 21.7956C7.27735 22.6403 6.29203 23.8409 5.71018 25.2456C5.12833 26.6503 4.97609 28.196 5.27272 29.6873C5.56934 31.1785 6.3015 32.5483 7.37662 33.6234C8.45174 34.6985 9.82152 35.4307 11.3127 35.7273C12.804 36.0239 14.3497 35.8717 15.7544 35.2898C17.1591 34.708 18.3597 33.7227 19.2044 32.4585C20.0491 31.1942 20.5 29.7079 20.5 28.1875M12.8125 20.5H15.375M20.5 28.1875V25.625"
        stroke={props.selected ? '#000' : '#D1D1D1'}
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      />
      <path
        d="M20.5 25.625C23.3305 25.625 25.625 23.3305 25.625 20.5C25.625 17.6695 23.3305 15.375 20.5 15.375C17.6695 15.375 15.375 17.6695 15.375 20.5C15.375 23.3305 17.6695 25.625 20.5 25.625Z"
        stroke={props.selected ? '#000' : '#D1D1D1'}
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      />
      <path
        d="M13.6667 27.3333L16.2292 24.7708"
        stroke={props.selected ? '#000' : '#D1D1D1'}
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      />
      <path
        d="M24.7708 16.2292L27.3333 13.6667"
        stroke={props.selected ? '#000' : '#D1D1D1'}
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      />
      <path
        d="M13.6667 13.6667L16.2292 16.2292"
        stroke={props.selected ? '#000' : '#D1D1D1'}
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      />
      <path
        d="M24.7708 24.7708L27.3333 27.3333"
        stroke={props.selected ? '#000' : '#D1D1D1'}
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      />
    </svg>
  );
};

export const BarChart = (props) => {
  return (
    <svg
      width={props.width}
      height={props.height}
      viewBox="0 0 41 41"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        d="M5.125 5.125V35.875H35.875"
        stroke={props.selected ? '#000' : '#D1D1D1'}
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      />
      <path
        d="M30.75 29.0417V15.375"
        stroke={props.selected ? '#000' : '#D1D1D1'}
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      />
      <path
        d="M22.2083 29.0417V8.54175"
        stroke={props.selected ? '#000' : '#D1D1D1'}
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      />
      <path
        d="M13.6667 29.0417V23.9167"
        stroke={props.selected ? '#000' : '#D1D1D1'}
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      />
    </svg>
  );
};

export const Caution = () => {
  return (
    <svg
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        d="M12 22C17.523 22 22 17.523 22 12C22 6.477 17.523 2 12 2C6.477 2 2 6.477 2 12C2 17.523 6.477 22 12 22Z"
        stroke="#B5B5B5"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      />
      <path
        d="M9 12L11 14L15 10"
        stroke="#B5B5B5"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      />
    </svg>
  );
};

export const Warning = () => {
  return (
    <svg
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <rect width="24" height="24" fill="white" />
      <path
        d="M12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22Z"
        stroke="#FFC909"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      />
      <path
        d="M12 8V12"
        stroke="#FFC909"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      />
      <path
        d="M12 16H12.01"
        stroke="#FFC909"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      />
    </svg>
  );
};

export const Notice = () => {
  return (
    <svg
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        d="M7.86 2H16.14L22 7.86V16.14L16.14 22H7.86L2 16.14V7.86L7.86 2Z"
        stroke="#E83030"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      />
      <path
        d="M15 9L9 15"
        stroke="#E83030"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      />
      <path
        d="M9 9L15 15"
        stroke="#E83030"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      />
    </svg>
  );
};

export const Add = (props) => {
  return (
    <svg
      fill="none"
      height={props.height}
      viewBox="0 0 32 32"
      width={props.width}
      xmlns="http://www.w3.org/2000/svg"
    >
      <rect fill="#fff" height="31" rx="5.5" width="31" x=".5" y=".5" />
      <rect height="31" rx="5.5" stroke="#e2e8f0" width="31" x=".5" y=".5" />
      <g
        stroke="#000"
        stroke-linecap="round"
        stroke-linejoin="round"
        stroke-width="1.33333"
      >
        <path d="m16 11.3334v9.3333" />
        <path d="m11.3333 16h9.3333" />
      </g>
    </svg>
  );
};

export const Settings = (props) => {
  return (
    <svg
      fill="none"
      height={props.height}
      viewBox="0 0 24 24"
      width={props.width}
      xmlns="http://www.w3.org/2000/svg"
    >
      <g
        stroke="#d1d1d1"
        stroke-linecap="round"
        stroke-linejoin="round"
        stroke-width="2"
      >
        <path d="m12 13c.5523 0 1-.4477 1-1s-.4477-1-1-1-1 .4477-1 1 .4477 1 1 1z" />
        <path d="m19 13c.5523 0 1-.4477 1-1s-.4477-1-1-1-1 .4477-1 1 .4477 1 1 1z" />
        <path d="m5 13c.55228 0 1-.4477 1-1s-.44772-1-1-1-1 .4477-1 1 .44772 1 1 1z" />
      </g>
    </svg>
  );
};

export const Camera = (props) => {
  return (
    <svg
      fill="none"
      height={props.height}
      viewBox="0 0 24 24"
      width={props.width}
      xmlns="http://www.w3.org/2000/svg"
    >
      <g
        stroke={props.selected ? '#000' : '#D1D1D1'}
        stroke-linecap="round"
        stroke-linejoin="round"
        stroke-width="2"
      >
        <path d="m14.5 4h-5l-2.5 3h-3c-.53043 0-1.03914.21071-1.41421.58579-.37508.37507-.58579.88378-.58579 1.41421v9c0 .5304.21071 1.0391.58579 1.4142.37507.3751.88378.5858 1.41421.5858h16c.5304 0 1.0391-.2107 1.4142-.5858s.5858-.8838.5858-1.4142v-9c0-.53043-.2107-1.03914-.5858-1.41421-.3751-.37508-.8838-.58579-1.4142-.58579h-3z" />
        <path d="m12 16c1.6569 0 3-1.3431 3-3s-1.3431-3-3-3-3 1.3431-3 3 1.3431 3 3 3z" />
      </g>
    </svg>
  );
};
