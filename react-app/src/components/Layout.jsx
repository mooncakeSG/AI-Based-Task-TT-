import Header from './Header';

const Layout = ({ children }) => {
  return (
    <div className="min-h-screen bg-gray-100 flex flex-col">
      <Header />
      <main className="flex-1 p-4 md:p-6 lg:p-8">
        <div className="max-w-6xl mx-auto h-full">
          {children}
        </div>
      </main>
      <footer className="bg-white border-t border-gray-200 py-4">
        <div className="container mx-auto px-4 text-center text-gray-600 text-sm">
          <p>© 2024 AI Task Assistant. Built with React & Tailwind CSS.</p>
        </div>
      </footer>
    </div>
  );
};

export default Layout; 