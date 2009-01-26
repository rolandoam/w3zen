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
  # constants
  SETTINGS = {
    :blog_title => "My Cool Blog",
    :blog_description => "a nice place",
    :time_format => "%Y-%m-%d",
    :data_dir => "/Users/rolando/Sites/test",
    :url => "http://myblog.com",
    :num_entries => 40,
    :file_extension => ".txt",
  }

  VERSION = "0.1.0"

  module Flavours
    # spit a list of entries in html format
    def html_list(entries)
      '<div class="entries">' <<
      entries.sort { |a,b| (b[:meta] ? b[:meta]['created_at'] : b[:date]) <=> (a[:meta] ? a[:meta]['created_at'] : a[:date]) }.map { |entry|
        "<div class=\"entry\">" <<
        "<div class=\"title\">" << "<a href=\"#{entry[:path].tr(' ', '+').gsub(/\..+$/, '')}\">#{entry[:title]}</a>" <<
        "<span class=\"date\">" << entry[:date].strftime(SETTINGS[:time_format]) << "</span></div></div>"
      }.join <<
      '</div>'
    end

    # spit a list of entries as rss
    def rss_list(entries)
    end

    # spit a single html entry
    def html_entry(entry_path)
      "<div class=\"post\">" <<
      RedCloth.new(File.read(entry_path)).to_html <<
      "</div>"
    end
  end

  include Flavours

  def initialize(cgi)
    path_info = (ENV['PATH_INFO'] || ENV['REQUEST_URI'] || '').gsub(/\?.*$/,'').split('/')
    path_info.shift
    fname = CGI::unescape("#{path_info.join('/')}".gsub(/\.+$/, ''))

    if fname.empty?
      cgi.out { 
        wrap do
          html_list(entries)
        end
      }
    elsif File.exists?(fpath = "#{SETTINGS[:data_dir]}/#{fname}#{SETTINGS[:file_extension]}") && File.file?(fpath)
      cgi.out { wrap { html_entry(fpath) } }
    else
      cgi.out('status' => "NOT_FOUND") { "File Not Found (#{fname})" }
    end
  end

  # wraps a block within a layout
  def wrap(&block)
    layout = ERB.new((File.read("#{SETTINGS[:data_dir]}/layout.rhtml") rescue ''))
    layout.result(binding)
  end

  # should return an array of hashes, with all the entries
  def entries
    now = Time.now
    Dir[SETTINGS[:data_dir] + "/**/*#{SETTINGS[:file_extension]}"].map { |f|
      file = File.new(f)
      title = File.basename(f, SETTINGS[:file_extension])
      meta = File.file?(meta_path = File.dirname(f) + "/#{title}.yaml") ? YAML.load(File.read(meta_path)) : nil
      {
        :title => title,
        :path  => file.path[SETTINGS[:data_dir].length, 100],
        :date  => file.ctime,
        :meta  => meta
      }
    }.reject { |e| e[:meta] && e[:meta]['publish_after'] && e[:meta]['publish_after'] < now }
  end
end

if __FILE__ == $0
  cgi = CGI.new
  begin
    W3Zen.new(cgi)
  rescue => err
    cgi.out("status" => "SERVER_ERROR") do
      "<h1>Something Terrible Happened!</h1>" <<
      "<pre>#{err}\n" <<
      err.backtrace.join("\n") <<
      "</pre>\n"
    end
  end
end
