import Layout from './components/Layout';
import ChatBox from './components/ChatBox';

function App() {
  return (
    <Layout>
      <div className="h-full flex flex-col">
        <div className="mb-6">
          <h2 className="text-xl md:text-2xl font-semibold text-gray-800 mb-2">
            Welcome to your AI Task Assistant
          </h2>
          <p className="text-gray-600 text-sm md:text-base">
            Start a conversation to manage your tasks, get help with planning, or ask questions. 
            The interface is optimized for both desktop and mobile use.
          </p>
        </div>
        
        <div className="flex-1 min-h-0">
          <div className="h-full bg-white rounded-lg shadow-sm border border-gray-200">
            <ChatBox />
          </div>
        </div>
      </div>
    </Layout>
  );
}

export default App;
