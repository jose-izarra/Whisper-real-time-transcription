'use client'
import { useState, useEffect } from 'react'


export default function Whisper() {

    // const [text, setText] = useState([])
    const [ transcripts, setTranscripts ] = useState<string[]>([])

    useEffect(() => {
        const getData = async () => {
            const res = await fetch('http://127.0.0.1:5000/api/whisper');
            const data = await res.json();

            console.log('data', data)
            setTranscripts(data);
            console.log('transcripts', transcripts, 'length: ', transcripts.length)
        }

        const interval = setInterval(() => {
            getData();
        }, 1000);

        return () => clearInterval(interval);
    }, [])


    return (
        <div className='h-screen flex flex-col items-center justify-end px-5'>

        {
            transcripts.length > 0 ? (
                <>
                    <h1 className="text-2xl font-bold">Whisper</h1>
                    <p className='font-sans text-lg'>{transcripts}</p>
                     
                </>
            ) : (
                <h1 className="text-2xl font-bold">No Whisper</h1>
            )
            

        }
            
        </div>
    )
}