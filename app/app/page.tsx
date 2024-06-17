import Whisper from "./components/whisper";



export default function Home() {
  const url = process.env.BACKEND_URL || 'bruh'

  return (
    <main className="">
      <Whisper url={url} />
    </main>
  );
}
