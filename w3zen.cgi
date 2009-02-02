#!/usr/bin/env ruby

require 'cgi'
require 'erb'
require 'yaml'
begin
  require 'rubygems'
  require 'redcloth'
rescue LoadError => err
  cgi.out("status" => "SERVER_ERROR") {
    "Error when requiring rubygems and/or RedCloth (#{err})"
  }
end

class W3Zen
  # some exceptions
  class W3ZenException < StandardError; end
  class FileNotFound < W3ZenException; end
  class SomeError < W3ZenException; end

  # constants
  SETTINGS = {
    :blog_title => "My Cool Blog",
    :blog_description => "a nice place",
    :time_format => "%Y-%m-%d",
    :data_dir => "/Users/rolando/Sites/test",
    :url => "http://test.local/~rolando",
    :num_entries => 40,
    :file_extension => ".txt",
    :default_flavour => "html"
  }

  CONTENT_TYPE = {
    "html" => "text/html",
    "rss"  => "text/xml"
  }

  VERSION = "0.1.0"

  module Flavours
    # spit a list of entries in html format
    def html_list(entries)
      '<div class="entries">' <<
      entries.sort { |a,b| (b[:meta] ? b[:meta]['created_at'] : b[:date]) <=> (a[:meta] ? a[:meta]['created_at'] : a[:date]) }.map { |entry|
        "<div class=\"entry\">" <<
        "<div class=\"title\">" << "<a href=\"#{entry[:link]}\">#{entry[:title]}</a>" <<
        "<span class=\"date\">" << entry[:date].strftime(SETTINGS[:time_format]) << "</span></div></div>"
      }.join <<
      '</div>'
    end

    # spit a list of entries as rss
    def rss_list(entries)
      entries.each { |entry|
        @xml.item do
          @xml.title entry[:title]
          @xml.pubDate entry[:meta] && entry[:meta]['created_at'] ? entry[:meta]['created_at'] : entry[:date]
          @xml.link entry[:link]
        end
      }
    end

    # spit a single html entry
    def html_entry(entry_path)
      <<-EOS.strip
<div class="post">
#{RedCloth.new(File.read(entry_path)).to_html}
</div>
      EOS
    end

    def rss_entry(entry_path)
      raise W3ZenException.new("Method Invalid")
    end
  end

  include Flavours

  def initialize(cgi)
    path_info = (ENV['PATH_INFO'] || ENV['REQUEST_URI'] || '').gsub(/\?.*$/,'').split('/')
    path_info.shift
    md = CGI::unescape("#{path_info.join('/')}").match(/^([^.]+)?(\.(\w+))?$/)
    flavour = md[3] || SETTINGS[:default_flavour]
    fname = md[1] || ''

    if fname.empty? || fname == "index"
      cgi.out("content-type" => CONTENT_TYPE[flavour]) { wrap(flavour) { safe_send("#{flavour}_list", entries) } }
    elsif File.exists?(fpath = "#{SETTINGS[:data_dir]}/#{fname}#{SETTINGS[:file_extension]}") && File.file?(fpath)
      cgi.out { wrap { safe_send("#{flavour}_entry", fpath) } }
    else
      raise FileNotFound.new(path_info.join('/'))
    end
  end

  # wraps a block within a layout
  def wrap(flavour = "html", &block)
    if flavour == "html"
      ERB.new((File.read("#{SETTINGS[:data_dir]}/layout.rhtml") rescue '')).result(binding)
    elsif flavour == "rss"
      require 'builder'
      @xml = Builder::XmlMarkup.new
      @xml.instruct! :xml, :version => "1.0"
      @xml.rss :version => "2.0" do
        fname = "#{SETTINGS[:data_dir]}/layout.rxml"
        eval(File.read(fname), binding, fname)
      end
    end
  end

  # should return an array of hashes, with all the entries
  def entries
    now = Time.now
    Dir[SETTINGS[:data_dir] + "/**/*#{SETTINGS[:file_extension]}"].map { |f|
      file = File.new(f)
      title = File.basename(f, SETTINGS[:file_extension])
      path  = file.path[SETTINGS[:data_dir].length, 100]
      meta = File.file?(meta_path = File.dirname(f) + "/#{title}.yaml") ? YAML.load(File.read(meta_path)) : nil
      {
        :title => title,
        :path  => path,
        :link  => "#{SETTINGS[:url]}#{path.tr(' ', '+').gsub(/\..+$/, '')}",
        :date  => file.ctime,
        :meta  => meta
      }
    }.reject { |e| e[:meta] && e[:meta]['publish_after'] && e[:meta]['publish_after'] < now }[0,SETTINGS[:num_entries]]
  end

  private
  def safe_send(meth, *args)
    if respond_to?(meth)
      send(meth, *args)
    else
      raise FileNotFound.new(meth)
    end
  end
end

if __FILE__ == $0
  cgi = CGI.new
  begin
    W3Zen.new(cgi)
  rescue Exception => err
    case err
    when W3Zen::FileNotFound
      cgi.out("status" => "NOT_FOUND") do
        <<-EOS
<h1>Error 404: File not found</h1>
#{err}
        EOS
      end
    when W3Zen::W3ZenException
      # output something more useful
      cgi.out("status" => "SERVER_ERROR") do
        <<-EOS
<h1>Ooops... It sure wasn't my fault!</h1>
(the error was: #{err})
        EOS
      end
    else
      # this might be a bug
      cgi.out("status" => "SERVER_ERROR") do
        <<-EOS
<h1>Something Terrible Happened!</h1>
<pre>#{err}
#{err.backtrace.join("\n")}
</pre>
        EOS
      end
    end
  end # rescue
end
