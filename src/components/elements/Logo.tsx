import Image from 'next/image'
import React from 'react'

function Logo() {
  return (
    <div>
      <Image
      src={"/Logo.png"}
      alt='Logo'
      width={150}
      height={50}
      className='object-cover'
      />
    </div>
  )
}

export default Logo
