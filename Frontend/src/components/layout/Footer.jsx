const Footer = () => {
    const currentYear = new Date().getFullYear()

    return (
        <footer className="bg-dark-card border-t border-dark-border mt-auto">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
                <div className="flex flex-col md:flex-row justify-between items-center gap-4">
                    {/* Copyright */}
                    <p className="text-sm text-gray-400">
                        © {currentYear} Accident Detection System. AIML Project.
                    </p>

                    {/* Tech Stack */}
                    <div className="flex items-center gap-2 text-sm text-gray-400">
                        <span>Built with</span>
                        <span className="font-semibold text-blue-500">React 19</span>
                        <span>•</span>
                        <span className="font-semibold text-blue-400">Vite</span>
                        <span>•</span>
                        <span className="font-semibold text-blue-300">Tailwind CSS</span>
                    </div>

                    {/* Version */}
                    <p className="text-xs text-gray-500">
                        v1.0.0
                    </p>
                </div>
            </div>
        </footer>
    )
}

export default Footer
