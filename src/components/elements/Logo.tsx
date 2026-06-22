import Image from 'next/image'
import React from 'react'

function Logo() {
  return (
    <div>
      <Image
      src={"/logo.png"}
      alt='Logo'
      width={150}
      height={50}
      className='object-contain'
      />
    </div>
  )
}

export default Logo
